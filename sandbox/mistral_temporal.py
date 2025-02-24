"""
acaba el proces pero clarament el fitxer de sortida al menys el stock propi esta malament, nomes hi ha un producte amb stock, pel
que fa al stock dels proveidors s'hauria de mirar de comparar amb el del excel
"""
import pandas as pd
import os
import socket

nombre_ordenador = socket.gethostname()
print("Nombre del ordenador:", nombre_ordenador)

# Rutas de los archivos
if nombre_ordenador == 'DESKTOP-8VJGJ8V':
    ruta_catalogo = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/triforfun-catalogo.csv'
    ruta_stock_propio = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/extract_produits_tailles.csv'
elif nombre_ordenador == 'THINKPAD':
    ruta_catalogo = 'G:/Otros ordenadores/Dell/DOCS/ONLINE/STOCKS_EXTERNS/triforfun-catalogo.csv'
    ruta_stock_propio = 'G:/Otros ordenadores/Dell/DOCS/ONLINE/STOCKS_EXTERNS/extract_produits_tailles.csv'

# Leer el catálogo principal
print("Leyendo el catálogo principal...")
catalogo = pd.read_csv(ruta_catalogo, encoding='utf-8', delimiter=';')

# Función para leer y procesar archivos CSV
def procesar_csv(ruta, delimitador, col_codigo, col_stock, encoding='latin1'):
    try:
        df = pd.read_csv(ruta, encoding=encoding, delimiter=delimitador)
    except UnicodeDecodeError:
        # Si falla con 'latin1', prueba con 'ISO-8859-1'
        df = pd.read_csv(ruta, encoding='ISO-8859-1', delimiter=delimitador)

    # Eliminar BOM si está presente en los nombres de las columnas
    df.columns = df.columns.str.replace('ï»¿', '', regex=False).str.strip('"')

    # Imprimir los nombres de las columnas para verificar
    print(f"Columnas en el archivo {ruta}: {df.columns}")

    df = df[[col_codigo, col_stock]]
    df.columns = ['codigo_barras', 'stock_proveedor']
    return df

# Función para leer y procesar archivos Excel
def procesar_excel(ruta, hoja, col_codigo, col_stock):
    df = pd.read_excel(ruta, sheet_name=hoja)
    df = df[[col_codigo, col_stock]]
    df.columns = ['codigo_barras', 'stock_proveedor']
    return df

# Procesar archivos de proveedores
proveedores = {
    'blunae': ('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/informe-maesarti.csv', ';', 'Código barras', 'Stock físico'),
    'sailfish': ('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/Availability.csv', ',', 'Variant Id', 'Instock'),
    'spiuk': ('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/stocks-spiuk.csv', ';', '--- EAN ---', '--- STOCK ---'),
    'cdc': ('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/STOCKcdc.CSV', ';', 'EAN', 'STOCK'),
    'somosdeportistas': ('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/STOCKSSD.CSV', ';', 'Código barras', 'Stock almacén ALM'),
    'myrco': ('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/Stock Myrco Sport.xlsx', 'Productos', 'Ean', 'Stock'),
    'hanker': ('C:/TFF/MARQUES/HANKER/2024/CODIS EAN HANKER.XLSX', 'Hanker', 'CÓDIGO DE BARRAS', 'STOCKPR')
}

# Diccionario para almacenar los stocks de proveedores
stocks_proveedores = {}

for proveedor, (ruta, delimitador, col_codigo, col_stock) in proveedores.items():
    print(f"Procesando archivo de {proveedor}...")
    if ruta.endswith('.csv'):
        df = procesar_csv(ruta, delimitador, col_codigo, col_stock)
    elif ruta.endswith('.xlsx'):
        df = procesar_excel(ruta, delimitador, col_codigo, col_stock)
    stocks_proveedores[proveedor] = df

# Procesar stock propio
print("Procesando stock propio...")
stock_propio = procesar_csv(ruta_stock_propio, ';', 'CÃ³digo de barras', 'TRI FOR FUN, S.L.')

# Actualizar el catálogo principal
print("Actualizando el catálogo principal...")
for index, row in catalogo.iterrows():
    codigo_barras = row['codigo_barras']

    # Actualizar stock propio
    stock_fila = stock_propio[stock_propio['codigo_barras'] == codigo_barras]
    if not stock_fila.empty:
        # Convertir a entero antes de asignar
        stock_value = stock_fila.iloc[0]['stock_proveedor']
        # Manejar valores no numéricos
        catalogo.at[index, 'stock'] = int(float(stock_value.replace(',', '.'))) if isinstance(stock_value, str) and stock_value.replace('.', '', 1).isdigit() else 0

    # Actualizar stock de proveedores
    for proveedor, df in stocks_proveedores.items():
        stock_fila = df[df['codigo_barras'] == codigo_barras]
        if not stock_fila.empty:
            # Convertir a entero antes de asignar
            stock_value = stock_fila.iloc[0]['stock_proveedor']
            # Manejar valores no numéricos
            catalogo.at[index, 'stock_proveedor'] = int(float(stock_value.replace(',', '.'))) if isinstance(stock_value, str) and stock_value.replace('.', '', 1).isdigit() else 0

# Guardar el catálogo actualizado
print("Guardando el catálogo actualizado...")
catalogo.to_csv(ruta_catalogo, index=False, encoding='utf-8')
print("Proceso completado.")
