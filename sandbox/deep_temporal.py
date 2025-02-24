"""
Proceso de actualización de stocks mejorado:
- Detección automática del delimitador
- Manejo robusto de archivos CSV
- Validación de columnas
"""
import pandas as pd
import os
import socket
from pathlib import Path
import csv

# Configuración inicial ========================================================
nombre_ordenador = socket.gethostname()
print(f"\n{'='*50}\nIniciando proceso en equipo: {nombre_ordenador}\n{'='*50}")

# Configuración de rutas base
if nombre_ordenador == 'DESKTOP-8VJGJ8V':
    ruta_base = Path('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/')
elif nombre_ordenador == 'THINKPAD':
    ruta_base = Path('G:/Otros ordenadores/Dell/DOCS/ONLINE/STOCKS_EXTERNS/')
else:
    raise ValueError(f"Ordenador no reconocido: {nombre_ordenador}")

# Configuración de archivos
config = {
    'catalogo': (ruta_base / 'triforfun-catalogo.csv', ';'),  # Especificar delimitador aquí
    'stock_propio': ruta_base / 'extract_produits_tailles.csv',
    'proveedores': {
        'blunae': (ruta_base / 'informe-maesarti.csv', ';', 'Código barras', 'Stock físico'),
        'sailfish': (ruta_base / 'Availability.csv', ',', 'Variant Id', 'Instock'),
        'spiuk': (ruta_base / 'stocks-spiuk.csv', ';', '--- EAN ---', '--- STOCK ---'),
        'cdc': (ruta_base / 'STOCKcdc.CSV', ';', 'EAN', 'STOCK'),
        'somosdeportistas': (ruta_base / 'STOCKSSD.CSV', ';', 'Código barras', 'Stock almacén ALM'),
        'myrco': (ruta_base / 'Stock Myrco Sport.xlsx', 'Productos', 'Ean', 'Stock'),
        'hanker': (ruta_base / 'CODIS EAN HANKER.XLSX', 'Hanker', 'CÓDIGO DE BARRAS', 'STOCKPR')
    }
}

# Funciones de procesamiento ==================================================
def detectar_delimitador(ruta):
    """Detecta automáticamente el delimitador de un archivo CSV"""
    with open(ruta, 'r', encoding='utf-8-sig') as f:
        sample = f.read(1024)
        if not sample:
            raise ValueError("El archivo está vacío o no se puede leer")
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            # Intentar con delimitadores comunes
            delimitadores_comunes = [',', ';', '\t', '|']
            for delim in delimitadores_comunes:
                if delim in sample:
                    return delim
            raise ValueError("No se pudo determinar el delimitador")
    return dialect.delimiter


def procesar_archivo(ruta, **kwargs):
    """Función unificada para procesar cualquier tipo de archivo"""
    try:
        if ruta.suffix == '.csv':
            # Detección automática de encoding y delimitador
            encodings = ['utf-8-sig', 'latin1', 'ISO-8859-1', 'cp1252']
            delimitador = kwargs.get('delimiter', None)
            for enc in encodings:
                try:
                    if not delimitador:
                        delimitador = detectar_delimitador(ruta)
                    df = pd.read_csv(ruta, encoding=enc, delimiter=delimitador)
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
        elif ruta.suffix == '.xlsx':
            df = pd.read_excel(ruta, sheet_name=kwargs.get('sheet_name'))
        else:
            raise ValueError("Formato de archivo no soportado")
    except Exception as e:
        raise ValueError(f"Error leyendo {ruta.name}: {str(e)}")

    # Limpieza de columnas
    df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df.columns = df.columns.str.lower().str.replace(r'[^\w]', ' ', regex=True).str.replace(' ', '_', regex=False)
    return df

def mapear_columnas(df, column_mapping):
    """Mapeo flexible de columnas"""
    selected_columns = {}
    for target, possibilities in column_mapping.items():
        for col in df.columns:
            if any(pos in col for pos in possibilities):
                selected_columns[col] = target
                break

    if len(selected_columns) != len(column_mapping):
        raise ValueError(f"No se encontraron todas las columnas requeridas. Columnas disponibles: {df.columns.tolist()}")
    
    return df.rename(columns=selected_columns)

# Procesamiento principal =====================================================
try:
    # 1. Cargar catálogo principal
    print("\nCargando catálogo base...")
    catalogo = procesar_archivo(config['catalogo'][0], delimiter=config['catalogo'][1])
    print("Columnas en catálogo:", catalogo.columns.tolist())    

    # 2. Procesar stock propio
    print("\nProcesando stock propio...")
    stock_propio = procesar_archivo(config['stock_propio'])
    print("Columnas en stock propio:", stock_propio.columns.tolist())
    stock_propio = mapear_columnas(stock_propio, {
        'codigo_barras': ['codigo_barras', 'codigo_de_barras', 'codigo'],
        'stock_propio': ['stock_propio', 'tri_for_fun__s_l_', 'stock']
    })
    stock_propio['stock_propio'] = stock_propio['stock_propio'].apply(convertir_stock)

    # 3. Fusionar stock propio con catálogo
    catalogo = catalogo.merge(
        stock_propio,
        on='codigo_barras',
        how='left'
    ).fillna({'stock_propio': 0})

    # 4. Procesar proveedores
    print("\nProcesando stocks de proveedores:")
    for proveedor, (ruta, delim, col_cod, col_stock) in config['proveedores'].items():
        print(f"- {proveedor.capitalize()}")
        df = procesar_archivo(ruta)
        df = mapear_columnas(df, {
            'codigo_barras': [col_cod.lower().strip()],
            'stock': [col_stock.lower().strip()]
        })
        
        df['stock'] = df['stock'].apply(convertir_stock)
        df = df.groupby('codigo_barras', as_index=False)['stock'].sum()
        
        catalogo = catalogo.merge(
            df,
            on='codigo_barras',
            how='left',
            suffixes=('', f'_{proveedor}')
        ).fillna({f'stock_{proveedor}': 0})

    # 5. Guardar resultados
    print("\nGuardando archivo actualizado...")
    catalogo.to_csv(config['catalogo'][0], index=False, encoding='utf-8-sig', sep=';')
    
    print(f"\n{'='*50}\nProceso completado correctamente!\nArchivo actualizado: {config['catalogo'][0]}\n{'='*50}")

except Exception as e:
    print(f"\n{'!'*50}\nError en el proceso: {str(e)}\n{'!'*50}")
    raise