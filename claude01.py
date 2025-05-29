#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Actualización de Stocks
Actualiza stocks de productos desde múltiples proveedores
Autor: Asistente Claude
Fecha: 2025
"""

import pandas as pd
import os
import logging
from datetime import datetime
import glob
import re
import chardet

class StockUpdater:
    def __init__(self, carpeta_archivos):
        self.carpeta_archivos = carpeta_archivos
        self.setup_logging()
        self.proveedores_config = {
            # 'Availability.csv': {'proveedor': 'sailfish', 'encoding': 'auto', 'sep': ',', 'campos': {'ean': 'Variant Id', 'stock': 'Instock'}},
            'Availability.csv': {'proveedor': 'sailfish', 'encoding': 'auto', 'sep': ',', 'campos': {'Variant Id', 'Instock'}},

            'CODIS EAN HANKER.xlsx': {'proveedor': 'hanker', 'campos': {'ean': 'ean', 'stock': 'stock'}},
            'extract_produits_tailles.csv': {'proveedor': 'local', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'codigo_barras', 'stock': 'stock'}},
            'head_Swimming_infostock.txt-1.csv': {'proveedor': 'mares', 'encoding': 'auto', 'sep': ',', 'campos': {'ean': 'ean', 'stock': 'stock'}},
            'informe-maesarti.csv': {'proveedor': 'blunae', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'ean', 'stock': 'disponibles'}},
            'Stock Myrco Sport.xlsx': {'proveedor': 'myrco', 'campos': {'ean': 'ean', 'stock': 'stock'}},
            'STOCKSSD.CSV': {'proveedor': 'somos_deportistas', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'ean', 'stock': 'stock'}},
            'stocks-spiuk.csv': {'proveedor': 'spiuk', 'encoding': 'auto', 'sep': ',', 'campos': {'ean': 'ean', 'stock': 'stock'}}
        }

    def setup_logging(self):
        """Configura el sistema de logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"stock_update_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def detectar_encoding(self, archivo):
        """Detecta automáticamente la codificación de un archivo"""
        try:
            with open(archivo, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            self.logger.warning(f"No se pudo detectar encoding de {archivo}: {e}")
            return 'utf-8'

    def normalizar_stock(self, valor):
        """Convierte valores de stock a números según las reglas especificadas"""
        if pd.isna(valor) or valor == '' or valor is None:
            return 0

        valor_str = str(valor).strip()

        # Casos especiales
        if valor_str.startswith('>'):
            try:
                num = int(re.findall(r'\d+', valor_str)[0])
                return num + 1
            except:
                return 6  # >5 por defecto
        elif valor_str.startswith('<'):
            try:
                num = int(re.findall(r'\d+', valor_str)[0])
                return max(2, num - 1)  # Mínimo 2 por prudencia
            except:
                return 2  # <5 por defecto

        # Intentar convertir a número
        try:
            return max(0, int(float(valor_str)))
        except:
            return 0

    def normalizar_ean(self, ean):
        """Normaliza el código EAN eliminando espacios y convirtiendo a string"""
        if pd.isna(ean):
            return None
        return str(ean).strip().replace(' ', '').replace('-', '')

    def leer_archivo_proveedor(self, archivo, config):
        """Lee un archivo de proveedor según su configuración"""
        try:
            ruta_completa = os.path.join(self.carpeta_archivos, archivo)

            # Verificar si el archivo existe
            if not os.path.exists(ruta_completa):
                # Buscar archivos con fecha para el caso especial
                patron = archivo.replace('.xlsx', '_*.xlsx').replace('.csv', '_*.csv')
                archivos_encontrados = glob.glob(os.path.join(self.carpeta_archivos, patron))
                if archivos_encontrados:
                    ruta_completa = max(archivos_encontrados, key=os.path.getmtime)  # El más reciente
                    self.logger.info(f"Usando archivo con fecha: {os.path.basename(ruta_completa)}")
                else:
                    self.logger.error(f"Archivo no encontrado: {archivo}")
                    return None

            # Leer según el tipo de archivo
            if archivo.endswith('.xlsx'):
                df = pd.read_excel(ruta_completa)
            else:
                encoding = config.get('encoding', 'utf-8')
                if encoding == 'auto':
                    encoding = self.detectar_encoding(ruta_completa)

                separador = config.get('sep', ',')
                df = pd.read_csv(ruta_completa, encoding=encoding, sep=separador, dtype=str)

            # Mapear columnas según configuración
            campos = config['campos']
            columnas_necesarias = [campos['ean'], campos['stock']]

            # Verificar que las columnas existen
            for col in columnas_necesarias:
                if col not in df.columns:
                    self.logger.error(f"Columna '{col}' no encontrada en {archivo}. Columnas disponibles: {list(df.columns)}")
                    return None

            # Seleccionar y renombrar columnas
            df_resultado = df[columnas_necesarias].copy()
            df_resultado.columns = ['ean', 'stock']

            # Normalizar datos
            df_resultado['ean'] = df_resultado['ean'].apply(self.normalizar_ean)
            df_resultado['stock'] = df_resultado['stock'].apply(self.normalizar_stock)

            # Eliminar filas sin EAN válido
            df_resultado = df_resultado.dropna(subset=['ean'])
            df_resultado = df_resultado[df_resultado['ean'] != '']

            # Agregar información del proveedor
            df_resultado['proveedor'] = config['proveedor']

            self.logger.info(f"Leído {archivo}: {len(df_resultado)} productos del proveedor {config['proveedor']}")
            return df_resultado

        except Exception as e:
            self.logger.error(f"Error leyendo {archivo}: {e}")
            return None

    def cargar_archivo_principal(self):
        """Carga el archivo principal de productos"""
        try:
            archivo_principal = os.path.join(self.carpeta_archivos, 'OT4_TOTS_ELS_PRODUCTES.csv')

            # Detectar encoding automáticamente
            encoding = self.detectar_encoding(archivo_principal)

            # Intentar diferentes separadores
            for sep in [';', ',', '\t']:
                try:
                    df = pd.read_csv(archivo_principal, encoding=encoding, sep=sep, dtype=str)
                    if 'codigo_barras' in df.columns:
                        break
                except:
                    continue

            if 'codigo_barras' not in df.columns:
                raise ValueError("No se encontró la columna 'codigo_barras'")

            # Normalizar EAN
            df['codigo_barras'] = df['codigo_barras'].apply(self.normalizar_ean)

            # Inicializar columnas de stock si no existen
            if 'stock' not in df.columns:
                df['stock'] = 0
            if 'stock_proveedor' not in df.columns:
                df['stock_proveedor'] = 0

            self.logger.info(f"Archivo principal cargado: {len(df)} productos")
            return df

        except Exception as e:
            self.logger.error(f"Error cargando archivo principal: {e}")
            return None

    def procesar_actualizacion(self):
        """Proceso principal de actualización"""
        self.logger.info("=== INICIANDO ACTUALIZACIÓN DE STOCKS ===")

        # Cargar archivo principal
        df_principal = self.cargar_archivo_principal()
        if df_principal is None:
            return False

        # Resetear stocks a 0
        df_principal['stock'] = 0
        df_principal['stock_proveedor'] = 0

        # Estadísticas
        productos_actualizados = set()
        productos_no_encontrados = set(df_principal['codigo_barras'].dropna())
        errores_lectura = []

        # Procesar cada proveedor
        for archivo, config in self.proveedores_config.items():
            self.logger.info(f"Procesando {archivo}...")

            df_proveedor = self.leer_archivo_proveedor(archivo, config)
            if df_proveedor is None:
                errores_lectura.append(archivo)
                continue

            # Actualizar stocks
            for _, row in df_proveedor.iterrows():
                ean = row['ean']
                stock = row['stock']
                proveedor = row['proveedor']

                # Buscar producto en archivo principal
                mask = df_principal['codigo_barras'] == ean
                if mask.any():
                    if proveedor == 'local':
                        df_principal.loc[mask, 'stock'] = stock
                    else:
                        df_principal.loc[mask, 'stock_proveedor'] = stock

                    productos_actualizados.add(ean)
                    productos_no_encontrados.discard(ean)

        # Generar archivo de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida = f"stocks_actualizados_{timestamp}.csv"

        df_salida = df_principal[['codigo_barras', 'stock', 'stock_proveedor']].copy()
        df_salida.columns = ['ean', 'stock', 'stock_proveedor']
        df_salida.to_csv(archivo_salida, index=False, encoding='utf-8', sep=';')

        # Generar reportes
        self.generar_reporte_final(
            productos_actualizados,
            productos_no_encontrados,
            errores_lectura,
            archivo_salida
        )

        return True

    def generar_reporte_final(self, actualizados, no_encontrados, errores, archivo_salida):
        """Genera el reporte final de la operación"""
        self.logger.info("=== REPORTE FINAL ===")
        self.logger.info(f"✅ Productos actualizados: {len(actualizados)}")
        self.logger.info(f"⚠️  Productos sin actualizar: {len(no_encontrados)}")
        self.logger.info(f"❌ Errores de lectura: {len(errores)}")
        self.logger.info(f"📄 Archivo generado: {archivo_salida}")

        if errores:
            self.logger.warning(f"Archivos con errores: {', '.join(errores)}")

        if no_encontrados and len(no_encontrados) < 50:  # Solo mostrar si no son demasiados
            self.logger.info(f"Productos no encontrados en proveedores: {len(no_encontrados)} productos")

        # Mensaje final en pantalla
        print("\n" + "="*60)
        print("🎯 ACTUALIZACIÓN DE STOCKS COMPLETADA")
        print("="*60)
        print(f"✅ Productos actualizados: {len(actualizados)}")
        print(f"⚠️  Productos sin stock: {len(no_encontrados)}")
        print(f"❌ Archivos con errores: {len(errores)}")
        print(f"📄 Archivo generado: {archivo_salida}")
        if errores:
            print(f"⚠️  ATENCIÓN: Errores en archivos: {', '.join(errores)}")
        print("="*60)

def main():
    """Función principal"""
    # Configurar la carpeta donde están los archivos
    CARPETA_ARCHIVOS = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS"

    # Verificar que la carpeta existe
    if not os.path.exists(CARPETA_ARCHIVOS):
        print(f"❌ Error: La carpeta {CARPETA_ARCHIVOS} no existe")
        return

    # Crear y ejecutar el actualizador
    updater = StockUpdater(CARPETA_ARCHIVOS)
    exito = updater.procesar_actualizacion()

    if exito:
        print("🎉 Proceso completado exitosamente")
    else:
        print("💥 El proceso terminó con errores")

if __name__ == "__main__":
    main()