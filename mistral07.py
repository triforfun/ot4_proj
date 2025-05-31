#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Actualización de Stocks
Actualiza stocks de productos desde múltiples proveedores.
Autor: Asistente Gemini (basado en tu código inicial)
Fecha: 2025
"""

import pandas as pd
import logging
from datetime import datetime
import glob
import re
import chardet
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class StockUpdater:
    def __init__(self, carpeta_entrada, carpeta_salida, carpeta_backup):
        """
        Inicializa el actualizador de stocks.

        Args:
            carpeta_entrada (str): Ruta a la carpeta donde se encuentran los archivos de stock de proveedores y el archivo principal.
            carpeta_salida (str): Ruta a la carpeta donde se guardará el archivo de stock actualizado.
            carpeta_backup (str): Ruta a la carpeta para guardar copias de seguridad del archivo principal.
        """
        self.carpeta_entrada = Path(carpeta_entrada)
        self.carpeta_salida = Path(carpeta_salida)
        self.carpeta_backup = Path(carpeta_backup)
        self.setup_logging()

        # Configuración de los proveedores
        self.proveedores_config = {
            'Availability.csv': {'proveedor': 'sailfish', 'encoding': 'auto', 'sep': ',', 'campos': {'ean': 'Variant Id', 'stock': 'Instock'}},
            'CODIS EAN HANKER.xlsx': {'proveedor': 'hanker', 'campos': {'ean': 'CÓDIGO DE BARRAS', 'stock': 'STOCKPR'}},
            'extract_produits_tailles.csv': {'proveedor': 'local', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'Código de barras', 'stock': 'TRI FOR FUN, S.L.'}},
            'head_Swimming_infostock.txt.csv.csv': {'proveedor': 'mares', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'EAN ', 'stock': 'QTY'}},
            'informe-maesarti.csv': {'proveedor': 'blunae', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'Código barras', 'stock': 'Stock físico'}},
            'Stock Myrco Sport.xlsx': {'proveedor': 'myrco', 'campos': {'ean': 'Ean', 'stock': 'Stock'}},
            'STOCKSSD.CSV': {'proveedor': 'somos_deportistas', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'Código barras', 'stock': 'Stock almacén ALM'}},
            'stocks-spiuk.csv': {'proveedor': 'spiuk', 'encoding': 'auto', 'sep': ';', 'quotechar': '"', 'campos': {'ean': '--- EAN ---', 'stock': '--- STOCK ---'}},
            'HOKA FW24 Especialista.xlsx': {'proveedor': 'running_king', 'campos': {'ean': 'UPC', 'stock': 'Quantity Available'}},
            'HOKA SS25 Especialista.xlsx': {'proveedor': 'running_king', 'campos': {'ean': 'UPC', 'stock': 'Quantity Available'}}
        }
        self.nombre_archivo_principal = 'ot4_tots_els_productes.csv'
        self.carpeta_hoka = Path("C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA")

        # Crear carpetas si no existen
        self.carpeta_salida.mkdir(parents=True, exist_ok=True)
        self.carpeta_backup.mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """Configura el sistema de logging para registrar la actividad del script."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"stock_update_{timestamp}.log"
        log_filepath = self.carpeta_salida / log_filename

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
        """
        Detecta automáticamente la codificación de un archivo CSV usando chardet.
        Si falla o la confianza es baja, se intenta con UTF-8 y Latin-1 como fallback.
        """
        try:
            with open(archivo, 'rb') as f:
                raw_data = f.read(10000)  # Leer una muestra suficiente
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']

            self.logger.debug(f"Chardet detectó '{encoding}' con confianza {confidence} para {archivo.name}")

            if encoding and confidence > 0.7:
                return encoding
            else:
                self.logger.warning(f"Confianza baja ({confidence}) o encoding no detectado para {archivo.name}. Intentando fallbacks.")
                try:
                    pd.read_csv(archivo, encoding='utf-8', nrows=5, sep=self.proveedores_config.get(archivo.name, {}).get('sep', ','))
                    return 'utf-8'
                except Exception:
                    try:
                        pd.read_csv(archivo, encoding='latin-1', nrows=5, sep=self.proveedores_config.get(archivo.name, {}).get('sep', ','))
                        return 'latin-1'
                    except Exception:
                        self.logger.error(f"No se pudo leer {archivo.name} con UTF-8 ni Latin-1. Usando UTF-8 por defecto.")
                        return 'utf-8'
        except Exception as e:
            self.logger.error(f"Error al detectar encoding de {archivo.name}: {e}. Usando UTF-8 por defecto.")
            return 'utf-8'

    def normalizar_stock(self, valor):
        """
        Convierte valores de stock a números enteros según las reglas especificadas:
        >N a N+1, <N a max(2, N-1), nulos/vacíos/negativos a 0.
        'SI' a 10, 'NO' a 0.
        """
        if pd.isna(valor) or str(valor).strip() == '' or valor is None:
            return 0

        valor_str = str(valor).strip().upper()  # Convertir a mayúsculas para comparar 'SI' y 'NO'

        if valor_str == 'SI':
            return 10
        elif valor_str == 'NO':
            return 0

        if valor_str.startswith('>'):
            match = re.search(r'\d+', valor_str)
            if match:
                return int(match.group(0)) + 1
            return 6

        if valor_str.startswith('<'):
            match = re.search(r'\d+', valor_str)
            if match:
                return max(2, int(match.group(0)) - 1)
            return 2

        try:
            numeric_val = re.sub(r'[^\d.]', '', valor_str)
            return max(0, int(float(numeric_val)))
        except ValueError:
            self.logger.warning(f"Valor de stock no numérico o inválido '{valor_str}'. Estableciendo a 0.")
            return 0

    def normalizar_ean(self, ean):
        """Normaliza el código EAN eliminando espacios, guiones y convirtiendo a string."""
        if pd.isna(ean):
            return None
        normalized_ean = str(ean).strip().replace(' ', '').replace('-', '')
        return normalized_ean if normalized_ean else None

    def eliminar_cero_izquierda(self, valor):
        """Elimina el cero a la izquierda de un valor."""
        if pd.isna(valor):
            return None
        valor_str = str(valor).strip()
        if valor_str.startswith('0') and len(valor_str) > 1:
            return valor_str[1:]
        return valor_str

    def leer_archivo_proveedor(self, archivo_nombre, config):
        """
        Lee un archivo de proveedor según su configuración (CSV o Excel),
        detecta encoding si es necesario y normaliza los datos.
        """
        self.logger.info(f"Intentando leer archivo: {archivo_nombre}")

        # Determinar la ruta completa del archivo
        if archivo_nombre in ['HOKA FW24 Especialista.xlsx', 'HOKA SS25 Especialista.xlsx']:
            ruta_completa = self.carpeta_hoka / archivo_nombre
        else:
            ruta_completa = self.carpeta_entrada / archivo_nombre

        if not ruta_completa.exists():
            self.logger.error(f"Archivo de proveedor no encontrado: {ruta_completa}. Saltando este proveedor.")
            return None

        df = None
        try:
            if archivo_nombre.endswith('.xlsx'):
                df = pd.read_excel(ruta_completa, dtype=str)
            else:
                encoding = config.get('encoding', 'auto')
                if encoding == 'auto':
                    encoding = self.detectar_encoding(ruta_completa)

                separador = config.get('sep', ',')
                quotechar = config.get('quotechar', '"')

                try:
                    df = pd.read_csv(ruta_completa, encoding=encoding, sep=separador, quotechar=quotechar, dtype=str)
                except Exception as e:
                    self.logger.warning(f"Fallo al leer {ruta_completa.name} con encoding '{encoding}' y separador '{separador}'. Intentando fallbacks.")
                    for enc in ['utf-8', 'latin-1', 'iso-8859-1']:
                        for sep in [',', ';', '\t', '|']:
                            try:
                                temp_df = pd.read_csv(ruta_completa, encoding=enc, sep=sep, quotechar=quotechar, dtype=str)
                                if len(temp_df.columns) > 1 or (len(temp_df.columns) == 1 and sep == ';'):
                                    df = temp_df
                                    self.logger.info(f"Éxito al leer {ruta_completa.name} con encoding '{enc}' y separador '{sep}'.")
                                    config['encoding'] = enc
                                    config['sep'] = sep
                                    break
                            except Exception:
                                continue
                        if df is not None:
                            break
                    if df is None:
                        self.logger.error(f"No se pudo leer el archivo CSV {ruta_completa.name} con ninguna combinación de encoding/separador probada. Error original: {e}")
                        return None
        except Exception as e:
            self.logger.error(f"Error general al leer {ruta_completa.name}: {e}")
            return None

        if df is None:
            return None

        campos_mapeo = config['campos']
        col_ean_original = campos_mapeo['ean']
        col_stock_original = campos_mapeo['stock']

        if col_ean_original not in df.columns or col_stock_original not in df.columns:
            self.logger.error(f"Faltan columnas esenciales en {ruta_completa.name}. Se esperaban '{col_ean_original}' y '{col_stock_original}'. Columnas disponibles: {list(df.columns)}")
            return None

        df_resultado = df[[col_ean_original, col_stock_original]].copy()
        df_resultado.columns = ['ean', 'stock']

        # Eliminar el cero a la izquierda en la columna EAN para los archivos de HOKA
        if archivo_nombre in ['HOKA FW24 Especialista.xlsx', 'HOKA SS25 Especialista.xlsx']:
            df_resultado['ean'] = df_resultado['ean'].apply(self.eliminar_cero_izquierda)

        df_resultado['ean'] = df_resultado['ean'].apply(self.normalizar_ean)
        df_resultado['stock'] = df_resultado['stock'].apply(self.normalizar_stock)

        df_resultado.dropna(subset=['ean'], inplace=True)

        df_resultado['stock'] = df_resultado['stock'].astype(int)

        df_resultado['proveedor'] = config['proveedor']

        self.logger.info(f"Leído {ruta_completa.name}: {len(df_resultado)} productos del proveedor {config['proveedor']}")
        return df_resultado

    def cargar_archivo_principal(self):
        """
        Carga el archivo principal de productos y realiza una copia de seguridad.
        Detecta automáticamente la codificación y el separador.
        """
        archivo_principal_path = self.carpeta_entrada / self.nombre_archivo_principal

        if not archivo_principal_path.exists():
            self.logger.critical(f"Archivo principal '{self.nombre_archivo_principal}' no encontrado en {self.carpeta_entrada}. El proceso no puede continuar.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.nombre_archivo_principal.replace('.csv', '')}_backup_{timestamp}.csv"
        backup_filepath = self.carpeta_backup / backup_filename
        try:
            shutil.copy2(archivo_principal_path, backup_filepath)
            self.logger.info(f"Copia de seguridad del archivo principal creada en: {backup_filepath}")
        except Exception as e:
            self.logger.error(f"Error al crear copia de seguridad del archivo principal: {e}")

        df = None
        encoding = self.detectar_encoding(archivo_principal_path)

        for sep in [';', ',', '\t', '|']:
            try:
                temp_df = pd.read_csv(archivo_principal_path, encoding=encoding, sep=sep, dtype=str)
                if 'codigo_barras' in temp_df.columns:
                    df = temp_df
                    self.logger.info(f"Archivo principal cargado con encoding '{encoding}' y separador '{sep}'.")
                    break
            except Exception:
                continue

        if df is None:
            self.logger.critical(f"No se pudo cargar el archivo principal '{self.nombre_archivo_principal}' con ninguna configuración probada. Asegúrate de que el formato sea correcto y tenga la columna 'codigo_barras'.")
            return None

        if 'codigo_barras' not in df.columns:
            self.logger.critical(f"La columna 'codigo_barras' no se encontró en el archivo principal. Columnas disponibles: {list(df.columns)}. El proceso no puede continuar.")
            return None

        df['codigo_barras'] = df['codigo_barras'].apply(self.normalizar_ean)
        df.dropna(subset=['codigo_barras'], inplace=True)

        if 'stock' not in df.columns:
            df['stock'] = 0
        else:
            df['stock'] = df['stock'].apply(self.normalizar_stock)

        if 'stock_proveedor' not in df.columns:
            df['stock_proveedor'] = 0
        else:
            df['stock_proveedor'] = df['stock_proveedor'].apply(self.normalizar_stock)

        df['stock'] = df['stock'].astype(int)
        df['stock_proveedor'] = df['stock_proveedor'].astype(int)

        self.logger.info(f"Archivo principal '{self.nombre_archivo_principal}' cargado: {len(df)} productos.")
        return df

    def generar_informe_sin_match_proveedores(self, df_principal, eans_con_match):
        """
        Genera un archivo CSV con la información de los productos que no tienen match en los proveedores (excluyendo extract_produits_tailles.csv).
        """
        productos_sin_match_proveedores = df_principal[~df_principal['codigo_barras'].isin(eans_con_match)]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida_nombre = f"productos_sin_match_proveedores_{timestamp}.csv"
        archivo_salida_path = self.carpeta_salida / archivo_salida_nombre

        try:
            productos_sin_match_proveedores.to_csv(archivo_salida_path, index=False, encoding='utf-8', sep=';')
            self.logger.info(f"Archivo de productos sin match en proveedores generado exitosamente: {archivo_salida_path}")
        except Exception as e:
            self.logger.error(f"Error al escribir el archivo de productos sin match en proveedores '{archivo_salida_nombre}': {e}")

    def generar_informe_sin_match_local(self, df_principal, eans_en_local):
        """
        Genera un archivo CSV con la información de los productos que no tienen match en extract_produits_tailles.csv.
        """
        productos_sin_match_local = df_principal[~df_principal['codigo_barras'].isin(eans_en_local)]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida_nombre = f"productos_sin_match_local_{timestamp}.csv"
        archivo_salida_path = self.carpeta_salida / archivo_salida_nombre

        try:
            productos_sin_match_local.to_csv(archivo_salida_path, index=False, encoding='utf-8', sep=';')
            self.logger.info(f"Archivo de productos sin match en local generado exitosamente: {archivo_salida_path}")
        except Exception as e:
            self.logger.error(f"Error al escribir el archivo de productos sin match en local '{archivo_salida_nombre}': {e}")

    def procesar_actualizacion(self):
        """
        Proceso principal de actualización de stocks.
        """
        self.logger.info("=== INICIANDO ACTUALIZACIÓN DE STOCKS ===")

        df_principal = self.cargar_archivo_principal()
        if df_principal is None:
            self.logger.critical("Fallo al cargar el archivo principal. Terminando el proceso.")
            return False

        df_principal['stock'] = 0
        df_principal['stock_proveedor'] = 0

        eans_con_match_proveedores = set()
        eans_en_local = set()
        archivos_con_errores = []

        ean_to_idx = pd.Series(df_principal.index, index=df_principal['codigo_barras']).to_dict()

        local_config = self.proveedores_config.get('extract_produits_tailles.csv')
        if local_config:
            self.logger.info("Procesando stock local (extract_produits_tailles.csv)...")
            df_local = self.leer_archivo_proveedor('extract_produits_tailles.csv', local_config)
            if df_local is not None:
                for ean, stock in df_local[['ean', 'stock']].values:
                    idx = ean_to_idx.get(ean)
                    if idx is not None:
                        df_principal.loc[idx, 'stock'] = stock
                        eans_en_local.add(ean)
                eans_con_match_proveedores.update(eans_en_local)
            else:
                archivos_con_errores.append('extract_produits_tailles.csv')

        def procesar_proveedor(archivo_nombre, config):
            self.logger.info(f"Procesando archivo de proveedor: {archivo_nombre}")
            df_proveedor = self.leer_archivo_proveedor(archivo_nombre, config)
            if df_proveedor is None:
                archivos_con_errores.append(archivo_nombre)
                return
            for ean, stock in df_proveedor[['ean', 'stock']].values:
                idx = ean_to_idx.get(ean)
                if idx is not None:
                    df_principal.loc[idx, 'stock_proveedor'] = stock
                    eans_con_match_proveedores.add(ean)

        with ThreadPoolExecutor() as executor:
            for archivo_nombre, config in self.proveedores_config.items():
                if config['proveedor'] == 'local':
                    continue
                executor.submit(procesar_proveedor, archivo_nombre, config)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida_nombre = f"stocks_actualizados_{timestamp}.csv"
        archivo_salida_path = self.carpeta_salida / archivo_salida_nombre

        df_salida = df_principal[['codigo_barras', 'stock', 'stock_proveedor']].copy()
        df_salida.columns = ['codigo_barras', 'stock', 'stock_proveedor']

        try:
            df_salida.to_csv(archivo_salida_path, index=False, encoding='utf-8', sep=';')
            self.logger.info(f"Archivo de salida generado exitosamente: {archivo_salida_path}")
        except Exception as e:
            self.logger.error(f"Error al escribir el archivo de salida '{archivo_salida_nombre}': {e}")
            return False

        productos_en_principal_total = len(df_principal)
        productos_sin_match_proveedores = productos_en_principal_total - len(eans_con_match_proveedores)
        productos_sin_match_local = productos_en_principal_total - len(eans_en_local)

        self.generar_informe_sin_match_proveedores(df_principal, eans_con_match_proveedores)
        self.generar_informe_sin_match_local(df_principal, eans_en_local)

        self.generar_reporte_final(
            len(eans_con_match_proveedores),
            productos_sin_match_proveedores,
            productos_sin_match_local,
            archivos_con_errores,
            archivo_salida_path
        )

        self.logger.info("=== ACTUALIZACIÓN DE STOCKS FINALIZADA ===")
        return True

    def generar_reporte_final(self, actualizados_count, sin_actualizar_proveedores, sin_actualizar_local, errores_archivos, archivo_salida_path):
        """Genera el reporte final de la operación tanto en el log como en consola."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🎯 REPORTE FINAL DE ACTUALIZACIÓN DE STOCKS")
        self.logger.info("="*60)
        self.logger.info(f"✅ Productos con stock actualizado: {actualizados_count}")
        self.logger.info(f"⚠️ Productos del archivo principal sin match en proveedores: {sin_actualizar_proveedores}")
        self.logger.info(f"⚠️ Productos del archivo principal sin match en local: {sin_actualizar_local}")
        self.logger.info(f"❌ Archivos de proveedor con errores de lectura: {len(errores_archivos)}")
        self.logger.info(f"📄 Archivo de salida generado en: {archivo_salida_path}")

        if errores_archivos:
            self.logger.warning(f"Detalles de archivos con errores: {', '.join(errores_archivos)}")

        print("\n" + "="*60)
        print("🎯 ACTUALIZACIÓN DE STOCKS COMPLETADA")
        print("="*60)
        print(f"✅ Productos con stock actualizado: {actualizados_count}")
        print(f"⚠️ Productos del archivo principal sin match en proveedores: {sin_actualizar_proveedores}")
        print(f"⚠️ Productos del archivo principal sin match en local: {sin_actualizar_local}")
        print(f"❌ Archivos de proveedor con errores de lectura: {len(errores_archivos)}")
        print(f"📄 Archivo de salida generado en: {archivo_salida_path}")
        if errores_archivos:
            print(f"⚠️ ATENCIÓN: Se encontraron errores en los siguientes archivos de proveedor: {', '.join(errores_archivos)}")
        print("="*60)

def main():
    """Función principal para ejecutar el actualizador de stocks."""
    CARPETA_ENTRADA = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS"
    CARPETA_SALIDA = "C:/TFF/DOCS/ONLINE/STOCKS_PROCESADOS"
    CARPETA_BACKUP = "C:/TFF/DOCS/ONLINE/STOCKS_BACKUP"

    if not Path(CARPETA_ENTRADA).exists():
        print(f"❌ Error: La carpeta de entrada '{CARPETA_ENTRADA}' no existe. Por favor, créala o verifica la ruta.")
        return

    Path(CARPETA_SALIDA).mkdir(parents=True, exist_ok=True)
    Path(CARPETA_BACKUP).mkdir(parents=True, exist_ok=True)

    updater = StockUpdater(CARPETA_ENTRADA, CARPETA_SALIDA, CARPETA_BACKUP)
    exito = updater.procesar_actualizacion()

    if exito:
        updater.logger.info("🎉 Proceso completado exitosamente.")
    else:
        updater.logger.critical("💥 El proceso terminó con errores críticos.")

if __name__ == "__main__":
    main()
