"""
actualitzacio automatica stocks
"""

import pandas as pd
import os

# Ruta de los archivos
directory_hanker = 'C:/TFF/MARQUES/HANKER/2024/'
directory = r'C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS'
log_file = os.path.join(directory, 'errors.log')

# Función para leer archivos CSV y manejar errores de formato
def read_csv_with_errors(file_path, delimiter=';', encoding='ISO-8859-1'):
    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, on_bad_lines='warn')
        return df
    except Exception as e:
        with open(log_file, 'a') as f:
            f.write(f"Error reading {file_path} with encoding {encoding}: {e}\n")
        return pd.DataFrame()

# Función para actualizar el stock
def update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_df, proveedor_code_column, proveedor_stock_column):
    # Actualizar el stock propio
    stock_auto_df = stock_auto_df.merge(extract_produits_tailles_df[['Código de barras', 'TRI FOR FUN, S.L.']],
                                        left_on='codigo_barras', right_on='Código de barras', how='left')
    stock_auto_df['stock'] = stock_auto_df['TRI FOR FUN, S.L.'].fillna(0)

    # Actualizar el stock del proveedor
    stock_auto_df = stock_auto_df.merge(proveedor_df[[proveedor_code_column, proveedor_stock_column]],
                                        left_on='codigo_barras', right_on=proveedor_code_column, how='left')
    stock_auto_df['stock_proveedor'] = stock_auto_df[proveedor_stock_column].fillna(0)

    return stock_auto_df

# Leer el archivo stock_auto.csv
stock_auto_path = os.path.join(directory, 'stock_auto.csv')
stock_auto_df = read_csv_with_errors(stock_auto_path)

# Leer el archivo extract_produits_tailles.csv
extract_produits_tailles_path = os.path.join(directory, 'extract_produits_tailles.csv')
extract_produits_tailles_df = read_csv_with_errors(extract_produits_tailles_path)

# Leer los archivos de los proveedores
proveedor_mares_df = read_csv_with_errors(os.path.join(directory, 'head_Swimming_infostock.txt.csv'))
proveedor_blunae_df = read_csv_with_errors(os.path.join(directory, 'informe-maesarti.csv'))
proveedor_spiuk_df = read_csv_with_errors(os.path.join(directory, 'stocks-spiuk.csv'))
proveedor_myrco_df = pd.read_excel(os.path.join(directory, 'Stock Myrco Sport.xlsx'), sheet_name='Productos')
proveedor_sailfish_df = read_csv_with_errors(os.path.join(directory, 'Availability.csv'))
proveedor_somosdeportistas_df = read_csv_with_errors(os.path.join(directory, 'STOCKSSD.CSV'))
proveedor_hanker_df = pd.read_excel(os.path.join(directory_hanker, 'CODIS EAN HANKER.xlsx'), sheet_name='Hanker')

# Actualizar el stock con cada proveedor
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_mares_df, 'EAN', 'QTY')
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_blunae_df, 'Código barras', 'Stock físico')
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_spiuk_df, '--- EAN ---', '--- STOCK ---')
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_myrco_df, 'Ean', 'Stock')
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_sailfish_df, 'Variant id', 'instock')
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_somosdeportistas_df, 'Código barras', 'Stock almacén ALM')
stock_auto_df = update_stock(stock_auto_df, extract_produits_tailles_df, proveedor_hanker_df, 'CÓDIGO DE BARRAS', 'STOCKPR')

# Guardar el archivo actualizado
stock_auto_df.to_csv(stock_auto_path, index=False, sep=';', encoding='utf-8')
