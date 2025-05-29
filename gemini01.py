#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Actualización de Stocks
Actualiza stocks de productos desde múltiples proveedores.
Autor: Asistente Gemini (basado en tu código inicial)
Fecha: 2025
"""

import pandas as pd
import os
import logging
from datetime import datetime
import glob
import re
import chardet
import shutil # Para copiar archivos, útil para el respaldo

class StockUpdater:
    def __init__(self, carpeta_entrada, carpeta_salida, carpeta_backup):
        """
        Inicializa el actualizador de stocks.

        Args:
            carpeta_entrada (str): Ruta a la carpeta donde se encuentran los archivos de stock de proveedores y el archivo principal.
            carpeta_salida (str): Ruta a la carpeta donde se guardará el archivo de stock actualizado.
            carpeta_backup (str): Ruta a la carpeta para guardar copias de seguridad del archivo principal.
        """
        self.carpeta_entrada = carpeta_entrada
        self.carpeta_salida = carpeta_salida
        self.carpeta_backup = carpeta_backup
        self.setup_logging()

        # Configuración de los proveedores
        # NOTA: Los nombres de los archivos deben coincidir exactamente con los de la carpeta.
        #       Se ha corregido el error en 'campos' para que sea un diccionario, no un set.
        #       Se ha añadido una configuración para el archivo principal aquí para mayor consistencia.
        self.proveedores_config = {
            'Availability.csv': {'proveedor': 'sailfish', 'encoding': 'auto', 'sep': ',', 'campos': {'ean': 'Variant Id', 'stock': 'Instock'}},
            'CODIS EAN HANKER.xlsx': {'proveedor': 'hanker', 'campos': {'ean': 'CÓDIGO DE BARRAS', 'stock': 'STOCKPR'}},
            'extract_produits_tailles.csv': {'proveedor': 'local', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'Código de barras', 'stock': 'TRI FOR FUN, S.L.'}},
            'head_Swimming_infostock.txt.csv.csv': {'proveedor': 'mares', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'EAN ', 'stock': 'QTY'}},
            'informe-maesarti.csv': {'proveedor': 'blunae', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'Código barras', 'stock': 'Stock físico'}},
            'Stock Myrco Sport.xlsx': {'proveedor': 'myrco', 'campos': {'ean': 'Ean', 'stock': 'Stock'}},
            'STOCKSSD.CSV': {'proveedor': 'somos_deportistas', 'encoding': 'auto', 'sep': ';', 'campos': {'ean': 'Código barras', 'stock': 'Stock almacén ALM'}},
            'stocks-spiuk.csv': {'proveedor': 'spiuk', 'encoding': 'auto', 'sep': ',', 'campos': {'ean': '---EAN---', 'stock': '--- STOCK ---'}}
        }
        self.nombre_archivo_principal = 'ot4_tots_els_productes.csv' # Asegurarse de que el nombre sea exacto

        # Crear carpetas si no existen
        os.makedirs(self.carpeta_salida, exist_ok=True)
        os.makedirs(self.carpeta_backup, exist_ok=True)

    def setup_logging(self):
        """Configura el sistema de logging para registrar la actividad del script."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"stock_update_{timestamp}.log"
        log_filepath = os.path.join(self.carpeta_salida, log_filename) # Guardar logs en la carpeta de salida

        # Reiniciar handlers si se llama varias veces (útil para pruebas o si la clase se instancia múltiples veces)
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filepath, encoding='utf-8'),
                logging.StreamHandler() # Para ver la salida también en consola
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
                raw_data = f.read(100000)  # Leer una porción grande para mejor detección
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']

            self.logger.debug(f"Chardet detectó '{encoding}' con confianza {confidence} para {os.path.basename(archivo)}")

            # Fallback si la confianza es baja
            if encoding and confidence > 0.7:
                return encoding
            else:
                self.logger.warning(f"Confianza baja ({confidence}) o encoding no detectado para {os.path.basename(archivo)}. Intentando fallbacks.")
                # Intentar con codificaciones comunes
                try:
                    pd.read_csv(archivo, encoding='utf-8', nrows=5, sep=self.proveedores_config.get(os.path.basename(archivo), {}).get('sep', ','))
                    return 'utf-8'
                except Exception:
                    try:
                        pd.read_csv(archivo, encoding='latin-1', nrows=5, sep=self.proveedores_config.get(os.path.basename(archivo), {}).get('sep', ','))
                        return 'latin-1'
                    except Exception:
                        self.logger.error(f"No se pudo leer {os.path.basename(archivo)} con UTF-8 ni Latin-1. Usando UTF-8 por defecto.")
                        return 'utf-8' # Último recurso
        except Exception as e:
            self.logger.error(f"Error al detectar encoding de {os.path.basename(archivo)}: {e}. Usando UTF-8 por defecto.")
            return 'utf-8'

    def normalizar_stock(self, valor):
        """
        Convierte valores de stock a números enteros según las reglas especificadas:
        >N a N+1, <N a max(2, N-1), nulos/vacíos/negativos a 0.
        """
        if pd.isna(valor) or str(valor).strip() == '' or valor is None:
            return 0

        valor_str = str(valor).strip()

        # Casos especiales para '>N' y '<N'
        if valor_str.startswith('>'):
            match = re.search(r'\d+', valor_str)
            if match:
                return int(match.group(0)) + 1
            return 6  # Valor por defecto para '>X' si no se detecta número

        if valor_str.startswith('<'):
            match = re.search(r'\d+', valor_str)
            if match:
                return max(2, int(match.group(0)) - 1)
            return 2  # Valor por defecto para '<X' si no se detecta número

        # Intentar convertir a número
        try:
            # Eliminar posibles caracteres no numéricos que no sean el punto decimal para floats
            numeric_val = re.sub(r'[^\d.]', '', valor_str)
            return max(0, int(float(numeric_val))) # Convertir a float primero para manejar decimales
        except ValueError:
            self.logger.warning(f"Valor de stock no numérico o inválido '{valor_str}'. Estableciendo a 0.")
            return 0

    def normalizar_ean(self, ean):
        """Normaliza el código EAN eliminando espacios, guiones y convirtiendo a string.
        Retorna None si el EAN es nulo o vacío después de la normalización."""
        if pd.isna(ean):
            return None
        normalized_ean = str(ean).strip().replace(' ', '').replace('-', '')
        return normalized_ean if normalized_ean else None # Devuelve None si queda vacío

    def leer_archivo_proveedor(self, archivo_nombre, config):
        """
        Lee un archivo de proveedor según su configuración (CSV o Excel),
        detecta encoding si es necesario y normaliza los datos.
        """
        self.logger.info(f"Intentando leer archivo: {archivo_nombre}")
        ruta_completa = os.path.join(self.carpeta_entrada, archivo_nombre)

        # Manejar caso de archivo con fecha (glob para encontrar el más reciente)
        if not os.path.exists(ruta_completa):
            patron_glob = os.path.join(self.carpeta_entrada, archivo_nombre.replace('.', '_*.'))
            archivos_encontrados = glob.glob(patron_glob)
            if archivos_encontrados:
                ruta_completa = max(archivos_encontrados, key=os.path.getmtime)
                self.logger.info(f"Usando archivo más reciente encontrado para '{archivo_nombre}': {os.path.basename(ruta_completa)}")
            else:
                self.logger.error(f"Archivo de proveedor no encontrado ni por nombre exacto ni por patrón de fecha: {archivo_nombre}. Saltando este proveedor.")
                return None

        df = None
        try:
            if archivo_nombre.endswith('.xlsx'):
                df = pd.read_excel(ruta_completa, dtype=str) # Leer todo como string para evitar conversiones automáticas
            else: # CSV
                encoding = config.get('encoding', 'auto')
                if encoding == 'auto':
                    encoding = self.detectar_encoding(ruta_completa)

                separador = config.get('sep', ',')

                # Intentar leer el CSV con el separador y encoding detectado/configurado
                try:
                    df = pd.read_csv(ruta_completa, encoding=encoding, sep=separador, dtype=str)
                except Exception as e:
                    self.logger.warning(f"Fallo al leer {os.path.basename(ruta_completa)} con encoding '{encoding}' y separador '{separador}'. Intentando fallbacks.")
                    # Fallback para separadores y encodings si el primero falla
                    for enc in ['utf-8', 'latin-1', 'iso-8859-1']:
                        for sep in [',', ';', '\t', '|']:
                            try:
                                temp_df = pd.read_csv(ruta_completa, encoding=enc, sep=sep, dtype=str)
                                # Verificar si hay al menos 2 columnas o si el separador funcionó bien
                                if len(temp_df.columns) > 1 or (len(temp_df.columns) == 1 and sep == ','):
                                    df = temp_df
                                    self.logger.info(f"Éxito al leer {os.path.basename(ruta_completa)} con encoding '{enc}' y separador '{sep}'.")
                                    config['encoding'] = enc # Actualizar configuración para futuras ejecuciones (opcional)
                                    config['sep'] = sep
                                    break
                            except Exception:
                                continue
                        if df is not None:
                            break
                    if df is None:
                        self.logger.error(f"No se pudo leer el archivo CSV {os.path.basename(ruta_completa)} con ninguna combinación de encoding/separador probada. Error original: {e}")
                        return None
        except Exception as e:
            self.logger.error(f"Error general al leer {os.path.basename(ruta_completa)}: {e}")
            return None

        if df is None: # Si por algún motivo no se pudo cargar el DF
            return None

        campos_mapeo = config['campos'] # Diccionario {'ean': 'nombre_col_ean', 'stock': 'nombre_col_stock'}
        col_ean_original = campos_mapeo['ean']
        col_stock_original = campos_mapeo['stock']

        # Verificar que las columnas existen en el DataFrame cargado
        if col_ean_original not in df.columns or col_stock_original not in df.columns:
            self.logger.error(f"Faltan columnas esenciales en {os.path.basename(ruta_completa)}. Se esperaban '{col_ean_original}' y '{col_stock_original}'. Columnas disponibles: {list(df.columns)}")
            return None

        # Seleccionar y renombrar columnas relevantes
        df_resultado = df[[col_ean_original, col_stock_original]].copy()
        df_resultado.columns = ['ean', 'stock']

        # Normalizar EAN y Stock
        df_resultado['ean'] = df_resultado['ean'].apply(self.normalizar_ean)
        df_resultado['stock'] = df_resultado['stock'].apply(self.normalizar_stock)

        # Eliminar filas con EAN nulo después de normalización
        df_resultado.dropna(subset=['ean'], inplace=True)

        # Asegurarse de que el stock sea entero
        df_resultado['stock'] = df_resultado['stock'].astype(int)

        # Agregar información del proveedor
        df_resultado['proveedor'] = config['proveedor']

        self.logger.info(f"Leído {os.path.basename(ruta_completa)}: {len(df_resultado)} productos del proveedor {config['proveedor']}")
        return df_resultado

    def cargar_archivo_principal(self):
        """
        Carga el archivo principal de productos y realiza una copia de seguridad.
        Detecta automáticamente la codificación y el separador.
        """
        archivo_principal_path = os.path.join(self.carpeta_entrada, self.nombre_archivo_principal)

        if not os.path.exists(archivo_principal_path):
            self.logger.critical(f"Archivo principal '{self.nombre_archivo_principal}' no encontrado en {self.carpeta_entrada}. El proceso no puede continuar.")
            return None

        # Hacer copia de seguridad
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.nombre_archivo_principal.replace('.csv', '')}_backup_{timestamp}.csv"
        backup_filepath = os.path.join(self.carpeta_backup, backup_filename)
        try:
            shutil.copy2(archivo_principal_path, backup_filepath)
            self.logger.info(f"Copia de seguridad del archivo principal creada en: {backup_filepath}")
        except Exception as e:
            self.logger.error(f"Error al crear copia de seguridad del archivo principal: {e}")
            # El proceso puede continuar, pero se notifica el error

        df = None
        encoding = self.detectar_encoding(archivo_principal_path) # Usar detección de encoding

        # Intentar con separadores comunes
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

        # Normalizar EAN en el archivo principal
        df['codigo_barras'] = df['codigo_barras'].apply(self.normalizar_ean)
        df.dropna(subset=['codigo_barras'], inplace=True) # Eliminar filas sin EAN válido en el principal

        # Inicializar columnas de stock si no existen o asegurarse de que sean numéricas
        if 'stock' not in df.columns:
            df['stock'] = 0
        else:
            df['stock'] = df['stock'].apply(self.normalizar_stock) # Normalizar stock existente

        if 'stock_proveedor' not in df.columns:
            df['stock_proveedor'] = 0
        else:
            df['stock_proveedor'] = df['stock_proveedor'].apply(self.normalizar_stock) # Normalizar stock existente

        # Asegurarse de que las columnas de stock sean de tipo entero
        df['stock'] = df['stock'].astype(int)
        df['stock_proveedor'] = df['stock_proveedor'].astype(int)

        self.logger.info(f"Archivo principal '{self.nombre_archivo_principal}' cargado: {len(df)} productos.")
        return df

    def procesar_actualizacion(self):
        """
        Proceso principal de actualización de stocks:
        1. Carga el archivo principal.
        2. Reinicia los stocks a 0.
        3. Procesa cada archivo de proveedor, actualizando el DataFrame principal.
        4. Genera el archivo de salida con los stocks actualizados.
        5. Genera un reporte final.
        """
        self.logger.info("=== INICIANDO ACTUALIZACIÓN DE STOCKS ===")

        df_principal = self.cargar_archivo_principal()
        if df_principal is None:
            self.logger.critical("Fallo al cargar el archivo principal. Terminando el proceso.")
            return False

        # Reiniciar stocks a 0 antes de la actualización
        # Esto asegura que los productos que no se encuentren en los archivos de proveedor
        # o en el stock local tengan 0 unidades al final del proceso.
        self.logger.info("Reiniciando stocks de 'stock' y 'stock_proveedor' a 0 para todos los productos.")
        df_principal['stock'] = 0
        df_principal['stock_proveedor'] = 0

        # Para llevar un registro de lo que se actualiza y lo que no
        productos_con_stock_actualizado = set() # EANs que han recibido alguna actualización
        archivos_con_errores = []

        # Usar un diccionario para mapear EAN a la fila del DataFrame principal para actualizaciones más eficientes
        # Esto evita iterar sobre el DataFrame completo en cada actualización, lo cual es lento para 30k+ filas
        # El índice del DataFrame ya es eficiente para búsquedas si el EAN es el índice.
        # Si 'codigo_barras' no es el índice, podemos crear un mapeo:
        ean_to_idx = pd.Series(df_principal.index, index=df_principal['codigo_barras']).to_dict()

        # Procesar stock local (extract_produits_tailles.csv) primero
        local_config = self.proveedores_config.get('extract_produits_tailles.csv')
        if local_config:
            self.logger.info("Procesando stock local (extract_produits_tailles.csv)...")
            df_local = self.leer_archivo_proveedor('extract_produits_tailles.csv', local_config)
            if df_local is not None:
                # Actualizar stock local en el DataFrame principal
                for ean, stock in df_local[['ean', 'stock']].values:
                    idx = ean_to_idx.get(ean)
                    if idx is not None:
                        df_principal.loc[idx, 'stock'] = stock
                        productos_con_stock_actualizado.add(ean)
            else:
                archivos_con_errores.append('extract_produits_tailles.csv')
        else:
            self.logger.warning("Configuración para 'extract_produits_tailles.csv' no encontrada en proveedores_config.")


        # Procesar cada proveedor externo
        for archivo_nombre, config in self.proveedores_config.items():
            if config['proveedor'] == 'local': # Ya procesado
                continue

            self.logger.info(f"Procesando archivo de proveedor: {archivo_nombre}")
            df_proveedor = self.leer_archivo_proveedor(archivo_nombre, config)
            if df_proveedor is None:
                archivos_con_errores.append(archivo_nombre)
                continue

            # Actualizar stock_proveedor en el DataFrame principal
            for ean, stock in df_proveedor[['ean', 'stock']].values:
                idx = ean_to_idx.get(ean)
                if idx is not None:
                    df_principal.loc[idx, 'stock_proveedor'] = stock
                    productos_con_stock_actualizado.add(ean) # Un producto puede tener stock local y de proveedor

        # Generar archivo de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_salida_nombre = f"stocks_actualizados_{timestamp}.csv"
        archivo_salida_path = os.path.join(self.carpeta_salida, archivo_salida_nombre)

        # Seleccionar las columnas finales y renombrarlas si es necesario para la salida web
        df_salida = df_principal[['codigo_barras', 'stock', 'stock_proveedor']].copy()
        df_salida.columns = ['ean', 'stock', 'stock_proveedor'] # Asegurar nombres de columna para la web

        try:
            df_salida.to_csv(archivo_salida_path, index=False, encoding='utf-8', sep=';')
            self.logger.info(f"Archivo de salida generado exitosamente: {archivo_salida_path}")
        except Exception as e:
            self.logger.error(f"Error al escribir el archivo de salida '{archivo_salida_nombre}': {e}")
            return False

        # Generar reportes
        productos_en_principal_total = len(df_principal)
        productos_sin_actualizar = productos_en_principal_total - len(productos_con_stock_actualizado)

        self.generar_reporte_final(
            len(productos_con_stock_actualizado), # Cantidad de productos que sí se actualizaron
            productos_sin_actualizar,            # Productos que no encontraron match en proveedores
            archivos_con_errores,
            archivo_salida_path
        )

        self.logger.info("=== ACTUALIZACIÓN DE STOCKS FINALIZADA ===")
        return True

    def generar_reporte_final(self, actualizados_count, sin_actualizar_count, errores_archivos, archivo_salida_path):
        """Genera el reporte final de la operación tanto en el log como en consola."""
        self.logger.info("\n" + "="*60)
        self.logger.info("🎯 REPORTE FINAL DE ACTUALIZACIÓN DE STOCKS")
        self.logger.info("="*60)
        self.logger.info(f"✅ Productos con stock actualizado: {actualizados_count}")
        self.logger.info(f"⚠️  Productos del archivo principal sin match en proveedores: {sin_actualizar_count}")
        self.logger.info(f"❌ Archivos de proveedor con errores de lectura: {len(errores_archivos)}")
        self.logger.info(f"📄 Archivo de salida generado en: {archivo_salida_path}")

        if errores_archivos:
            self.logger.warning(f"Detalles de archivos con errores: {', '.join(errores_archivos)}")

        # Mensaje final en consola
        print("\n" + "="*60)
        print("🎯 ACTUALIZACIÓN DE STOCKS COMPLETADA")
        print("="*60)
        print(f"✅ Productos con stock actualizado: {actualizados_count}")
        print(f"⚠️  Productos del archivo principal sin match en proveedores: {sin_actualizar_count}")
        print(f"❌ Archivos de proveedor con errores de lectura: {len(errores_archivos)}")
        print(f"📄 Archivo de salida generado en: {archivo_salida_path}")
        if errores_archivos:
            print(f"⚠️  ATENCIÓN: Se encontraron errores en los siguientes archivos de proveedor: {', '.join(errores_archivos)}")
        print("="*60)

def main():
    """Función principal para ejecutar el actualizador de stocks."""
    # --- CONFIGURACIÓN DE CARPETAS ---
    # Es crucial que estas rutas sean correctas y existan.
    # Se recomienda usar rutas absolutas o relativas al script si el script se ejecuta desde su ubicación.
    # Ejemplo para Windows:
    CARPETA_ENTRADA = "C:\\TFF\\DOCS\\ONLINE\\STOCKS_EXTERNS"
    CARPETA_SALIDA = "C:\\TFF\\DOCS\\ONLINE\\STOCKS_PROCESADOS"
    CARPETA_BACKUP = "C:\\TFF\\DOCS\\ONLINE\\STOCKS_BACKUP"

    # Ejemplo para Linux/macOS:
    # CARPETA_ENTRADA = "/ruta/a/tus/stocks/externos"
    # CARPETA_SALIDA = "/ruta/a/tus/stocks/procesados"
    # CARPETA_BACKUP = "/ruta/a/tus/stocks/backup"
    # ---------------------------------

    # Verificar que las carpetas de entrada y backup existan antes de empezar
    if not os.path.exists(CARPETA_ENTRADA):
        print(f"❌ Error: La carpeta de entrada '{CARPETA_ENTRADA}' no existe. Por favor, créala o verifica la ruta.")
        return

    # Crear carpetas de salida y backup si no existen
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    os.makedirs(CARPETA_BACKUP, exist_ok=True)

    # Crear y ejecutar el actualizador
    updater = StockUpdater(CARPETA_ENTRADA, CARPETA_SALIDA, CARPETA_BACKUP)
    exito = updater.procesar_actualizacion()

    if exito:
        updater.logger.info("🎉 Proceso completado exitosamente.")
    else:
        updater.logger.critical("💥 El proceso terminó con errores críticos.")

if __name__ == "__main__":
    main()