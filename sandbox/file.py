"""
actualitzacio automatica stocks
"""

import pandas as pd
import os

# Ruta de los archivos
directory = r'C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS'
log_file = os.path.join(directory, 'errors.log')

# Función para leer archivos CSV y manejar errores de formato
def read_csv_with_errors(file_path, delimiter=';', encodings=['ISO-8859-1', 'latin1', 'cp1252']):
    for encoding in encodings:
        try:
            # Leer el archivo CSV
            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, on_bad_lines='warn')
            return df
        except Exception as e:
            with open(log_file, 'a') as f:
                f.write(f"Error reading {file_path} with encoding {encoding}: {e}\n")
    return pd.DataFrame()

# Función para actualizar el stock
def update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_df, proveedor_code_column_index, proveedor_stock_column_index):
    # Verificar los nombres de las columnas
    print("Columnas en extract_produits_tailles_df:", extract_produits_tailles_df.columns)
    print("Columnas en proveedor_df:", proveedor_df.columns)

    # Actualizar el stock propio usando la posición de la columna
    stock_auto_df = stock_auto_df.merge(
        extract_produits_tailles_df.iloc[:, [8, 12]],  # Usar la posición de las columnas
        left_on='codigo_barras', right_on=extract_produits_tailles_df.columns[8], how='left'
    )
    stock_auto_df['stock'] = stock_auto_df.iloc[:, -1].fillna(0)  # Usar la última columna agregada

    # Actualizar el stock del proveedor
    stock_auto_df = stock_auto_df.merge(
        proveedor_df.iloc[:, [proveedor_code_column_index, proveedor_stock_column_index]],
        left_on='codigo_barras', right_on=proveedor_df.columns[proveedor_code_column_index], how='left'
    )
    stock_auto_df['stock_proveedor'] = stock_auto_df.iloc[:, -1].fillna(0)  # Usar la última columna agregada

    return stock_auto_df

# Leer el archivo stock_auto.csv
stock_auto_path = os.path.join(directory, 'stock_auto.csv')
stock_auto_df = read_csv_with_errors(stock_auto_path)

# Leer el archivo extract_produits_tailles.csv
extract_produits_tailles_path = os.path.join(directory, 'extract_produits_tailles.csv')
extract_produits_tailles_df = read_csv_with_errors(extract_produits_tailles_path)

# Leer los archivos de los proveedores
proveedor_sailfish_df = read_csv_with_errors(os.path.join(directory, 'Availability.csv'))
proveedor_mares_df = read_csv_with_errors(os.path.join(directory, 'head_Swimming_infostock.txt.csv'))
proveedor_blunae_df = read_csv_with_errors(os.path.join(directory, 'informe-maesarti.csv'))
proveedor_spiuk_df = read_csv_with_errors(os.path.join(directory, 'stocks-spiuk.csv'))
proveedor_myrco_df = pd.read_excel(os.path.join(directory, 'Stock Myrco Sport.xlsx'), sheet_name='Productos')
# proveedor_sailfish_df = read_csv_with_errors(os.path.join(directory, 'Availability.csv'))
proveedor_somosdeportistas_df = read_csv_with_errors(os.path.join(directory, 'STOCKSSD.CSV'))

# Leer el archivo de Hanker desde su ubicación correcta
proveedor_hanker_path = r'C:\TFF\MARQUES\HANKER\2024\CODIS EAN HANKER.xlsx'
if os.path.exists(proveedor_hanker_path):
    proveedor_hanker_df = pd.read_excel(proveedor_hanker_path, sheet_name='Hanker')
else:
    with open(log_file, 'a') as f:
        f.write(f"File not found: {proveedor_hanker_path}\n")
    proveedor_hanker_df = pd.DataFrame()

# Actualizar el stock con cada proveedor
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_mares_df, 3, 7)  # EAN en la columna 4, QTY en la columna 8
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_blunae_df, 7, 2)  # Código barras en la columna 8, Stock físico en la columna 3
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_spiuk_df, 1, 3)  # EAN en la columna 2, STOCK en la columna 4
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_myrco_df, 0, 2)  # Ean en la columna 1, Stock en la columna 3
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_sailfish_df, 0, 1)  # Variant id en la columna 1, instock en la columna 2
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_somosdeportistas_df, 0, 1)  # Código barras en la columna 1, Stock almacén ALM en la columna 2
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_hanker_df, 0, 1)  # CÓDIGO DE BARRAS en la columna 1, STOCKPR en la columna 2

# Guardar el archivo actualizado
stock_auto_df.to_csv(stock_auto_path, index=False, sep=';', encoding='utf-8')
