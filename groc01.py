#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Actualización de Stocks
Actualiza stocks de productos desde múltiples proveedores.
Autor: [Tu Nombre]
Fecha: 2025
"""

import pandas as pd
import os
import logging
from datetime import datetime
import glob
import re
import chardet
import shutil
import json

class StockUpdater:
    def __init__(self, carpeta_entrada, carpeta_salida, carpeta_backup, config_path):
        """
        Inicializa el actualizador de stocks.

        Args:
            carpeta_entrada (str): Ruta a la carpeta de archivos de proveedores y principal.
            carpeta_salida (str): Ruta donde se guardará el archivo actualizado.
            carpeta_backup (str): Ruta para copias de seguridad.
            config_path (str): Ruta al archivo JSON de configuración de proveedores.
        """
        self.carpeta_entrada = carpeta_entrada
        self.carpeta_salida = carpeta_salida
        self.carpeta_backup = carpeta_backup
        self.config_path = config_path
        self.setup_logging()

        # Cargar configuración de proveedores desde JSON
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.proveedores_config = json.load(f)

        self.nombre_archivo_principal = 'ot4_tots_els_productes.csv'
        os.makedirs(self.carpeta_salida, exist_ok=True)
        os.makedirs(self.carpeta_backup, exist_ok=True)

    def setup_logging(self):
        """Configura el sistema de logging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"stock_update_{timestamp}.log"
        log_filepath = os.path.join(self.carpeta_salida, log_filename)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filepath, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def detectar_encoding(self, archivo):
        """Detecta la codificación de un archivo con fallbacks extendidos."""
        try:
            with open(archivo, 'rb') as f:
                raw_data = f.read(100000)
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']

            if encoding and confidence > 0.7:
                return encoding
            else:
                self.logger.warning(f"Confianza baja ({confidence}) para {os.path.basename(archivo)}. Usando fallbacks.")
                for enc in ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-15']:
                    try:
                        pd.read_csv(archivo, encoding=enc, nrows=5, sep=',')
                        return enc
                    except Exception:
                        continue
                self.logger.error(f"No se pudo detectar encoding para {os.path.basename(archivo)}. Usando UTF-8.")
                return 'utf-8'
        except Exception as e:
            self.logger.error(f"Error detectando encoding de {os.path.basename(archivo)}: {e}. Usando UTF-8.")
            return 'utf-8'

    def normalizar_stock(self, valor):
        """Normaliza valores de stock a enteros."""
        if pd.isna(valor) or str(valor).strip() == '':
            return 0

        valor_str = str(valor).strip()
        if valor_str.startswith('>'):
            match = re.search(r'\d+', valor_str)
            return int(match.group(0)) + 1 if match else 6
        if valor_str.startswith('<'):
            match = re.search(r'\d+', valor_str)
            return max(2, int(match.group(0)) - 1) if match else 2

        try:
            numeric_val = re.sub(r'[^\d.]', '', valor_str)
            return max(0, int(float(numeric_val)))
        except ValueError:
            self.logger.warning(f"Stock inválido '{valor_str}'. Establecido a 0.")
            return 0

    def normalizar_ean(self, ean):
        """Normaliza y valida códigos EAN."""
        if pd.isna(ean):
            return None
        normalized_ean = str(ean).strip().replace(' ', '').replace('-', '')
        if len(normalized_ean) == 13 and normalized_ean.isdigit():
            return normalized_ean
        self.logger.warning(f"EAN inválido: '{ean}'. Longitud o formato incorrecto.")
        return None

    def leer_archivo_proveedor(self, archivo_nombre, config):
        """Lee y normaliza datos de un archivo de proveedor."""
        self.logger.info(f"Leyendo archivo: {archivo_nombre}")
        ruta_completa = os.path.join(self.carpeta_entrada, archivo_nombre)

        if not os.path.exists(ruta_completa):
            patron_glob = os.path.join(self.carpeta_entrada, archivo_nombre.replace('.', '_[0-9]{8}.'))
            archivos_encontrados = glob.glob(patron_glob)
            if archivos_encontrados:
                ruta_completa = max(archivos_encontrados, key=os.path.getmtime)
                self.logger.info(f"Usando: {os.path.basename(ruta_completa)}")
            else:
                self.logger.error(f"Archivo no encontrado: {archivo_nombre}.")
                return None

        try:
            if archivo_nombre.endswith('.xlsx'):
                df = pd.read_excel(ruta_completa, dtype=str)
            else:
                encoding = self.detectar_encoding(ruta_completa) if config.get('encoding', 'auto') == 'auto' else config['encoding']
                sep = config.get('sep', ',')
                df = pd.read_csv(ruta_completa, encoding=encoding, sep=sep, dtype=str)
        except Exception as e:
            self.logger.error(f"Error leyendo {os.path.basename(ruta_completa)}: {e}")
            return None

        campos = config['campos']
        if campos['ean'] not in df.columns or campos['stock'] not in df.columns:
            self.logger.error(f"Faltan columnas en {os.path.basename(ruta_completa)}: {list(df.columns)}")
            return None

        df_resultado = df[[campos['ean'], campos['stock']]].copy()
        df_resultado.columns = ['ean', 'stock']
        df_resultado['ean'] = df_resultado['ean'].apply(self.normalizar_ean)
        df_resultado['stock'] = df_resultado['stock'].apply(self.normalizar_stock)
        df_resultado.dropna(subset=['ean'], inplace=True)
        df_resultado['stock'] = df_resultado['stock'].astype('int32')
        df_resultado['proveedor'] = config['proveedor']

        self.logger.info(f"Procesado {os.path.basename(ruta_completa)}: {len(df_resultado)} productos.")
        return df_resultado

    def cargar_archivo_principal(self):
        """Carga el archivo principal y realiza un backup."""
        archivo_principal_path = os.path.join(self.carpeta_entrada, self.nombre_archivo_principal)
        if not os.path.exists(archivo_principal_path):
            self.logger.critical(f"Archivo principal no encontrado: {self.nombre_archivo_principal}")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.carpeta_backup, f"{self.nombre_archivo_principal}_backup_{timestamp}.csv")
        try:
            shutil.copy2(archivo_principal_path, backup_path)
            self.logger.info(f"Backup creado: {backup_path}")
        except Exception as e:
            self.logger.error(f"Error en backup: {e}")

        encoding = self.detectar_encoding(archivo_principal_path)
        for sep in [';', ',', '\t', '|']:
            try:
                df = pd.read_csv(archivo_principal_path, encoding=encoding, sep=sep, dtype=str)
                if 'codigo_barras' in df.columns:
                    break
            except Exception:
                continue
        else:
            self.logger.critical(f"No se pudo cargar {self.nombre_archivo_principal}")
            return None

        df['codigo_barras'] = df['codigo_barras'].apply(self.normalizar_ean)
        df.dropna(subset=['codigo_barras'], inplace=True)
        if 'stock' in df.columns:
            df['stock'] = df['stock'].apply(self.normalizar_stock).astype('int32')
        else:
            df['stock'] = pd.Series([0] * len(df), dtype='int32')
        # df['stock'] = df.get('stock', 0).apply(self.normalizar_stock).astype('int32')
        df['stock_proveedor'] = df.get('stock_proveedor', 0).apply(self.normalizar_stock).astype('int32')

        self.logger.info(f"Cargado {self.nombre_archivo_principal}: {len(df)} productos.")
        return df

    def procesar_actualizacion(self):
        """Procesa la actualización de stocks."""
        self.logger.info("=== INICIANDO ACTUALIZACIÓN ===")
        df_principal = self.cargar_archivo_principal()
        if df_principal is None:
            return False

        df_principal['stock'] = 0
        df_principal['stock_proveedor'] = 0
        ean_to_idx = pd.Series(df_principal.index, index=df_principal['codigo_barras']).to_dict()
        productos_actualizados = set()
        errores_archivos = []

        for archivo_nombre, config in self.proveedores_config.items():
            df_proveedor = self.leer_archivo_proveedor(archivo_nombre, config)
            if df_proveedor is None:
                errores_archivos.append(archivo_nombre)
                continue
            target_col = 'stock' if config['proveedor'] == 'local' else 'stock_proveedor'
            for ean, stock in df_proveedor[['ean', 'stock']].values:
                idx = ean_to_idx.get(ean)
                if idx is not None:
                    df_principal.loc[idx, target_col] = stock
                    productos_actualizados.add(ean)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = os.path.join(self.carpeta_salida, f"stocks_actualizados_{timestamp}.csv")
        try:
            df_principal[['codigo_barras', 'stock', 'stock_proveedor']].to_csv(archivo_salida, index=False, encoding='utf-8', sep=';')
            self.logger.info(f"Archivo generado: {archivo_salida}")
        except Exception as e:
            self.logger.error(f"Error escribiendo salida: {e}")
            return False

        self.generar_reporte_final(len(productos_actualizados), len(df_principal) - len(productos_actualizados), errores_archivos, archivo_salida)
        self.logger.info("=== ACTUALIZACIÓN FINALIZADA ===")
        return True

    def generar_reporte_final(self, actualizados, sin_actualizar, errores, archivo_salida):
        """Genera un reporte final."""
        reporte = (
            f"\n{'='*60}\n"
            "🎯 REPORTE FINAL DE ACTUALIZACIÓN\n"
            f"{'='*60}\n"
            f"✅ Productos actualizados: {actualizados}\n"
            f"⚠️ Productos sin match: {sin_actualizar}\n"
            f"❌ Archivos con errores: {len(errores)}\n"
            f"📄 Salida: {archivo_salida}"
        )
        self.logger.info(reporte)
        if errores:
            self.logger.warning(f"Archivos con errores: {', '.join(errores)}")
        print(reporte)
        if errores:
            print(f"⚠️ Errores en: {', '.join(errores)}")
        print('='*60)

def main():
    """Ejecuta el actualizador de stocks."""
    CARPETA_ENTRADA = "C:\\TFF\\DOCS\\ONLINE\\STOCKS_EXTERNS"
    CARPETA_SALIDA = "C:\\TFF\\DOCS\\ONLINE\\STOCKS_PROCESADOS"
    CARPETA_BACKUP = "C:\\TFF\\DOCS\\ONLINE\\STOCKS_BACKUP"
    CONFIG_PATH = "proveedores_config.json"

    if not os.path.exists(CARPETA_ENTRADA):
        print(f"❌ Carpeta de entrada no encontrada: {CARPETA_ENTRADA}")
        return

    updater = StockUpdater(CARPETA_ENTRADA, CARPETA_SALIDA, CARPETA_BACKUP, CONFIG_PATH)
    exito = updater.procesar_actualizacion()
    updater.logger.info("🎉 Éxito!" if exito else "💥 Errores críticos.")

if __name__ == "__main__":
    main()