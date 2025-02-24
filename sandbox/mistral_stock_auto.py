import pandas as pd
import os
import sys

# Redirigir la salida estándar y de error a un archivo de registro
log_file = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/stock_auto_log.txt'
sys.stdout = open(log_file, 'w')
sys.stderr = open(log_file, 'a')

# Rutas de los ficheros
stock_auto_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/stock_auto.csv'
extract_produits_tailles_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/extract_produits_tailles.csv'
head_swimming_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/head_Swimming_infostock.txt.csv'
informe_maesarti_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/informe-maesarti.csv'
stocks_spiuk_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/stocks-spiuk.csv'
stocks_myrco_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/Stock Myrco Sport.xlsx'
availability_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/Availability.csv'
stockssd_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/STOCKSSD.CSV'
hanker_path = 'C:/TFF/MARQUES/HANKER/2024/CODIS EAN HANKER.xlsx'

# Verificar la existencia del archivo Stocks MyrcoSport.xlsx
if not os.path.exists(stocks_myrco_path):
    print(f"Error: El archivo {stocks_myrco_path} no existe.")
    sys.exit(1)

# Leer los ficheros con manejo de errores y codificación
try:
    stock_auto = pd.read_csv(stock_auto_path)
except pd.errors.ParserError as e:
    print(f"Error al leer {stock_auto_path}: {e}")
    raise

try:
    extract_produits_tailles = pd.read_csv(extract_produits_tailles_path, delimiter=',', on_bad_lines='warn', encoding='latin1')
except pd.errors.ParserError as e:
    print(f"Error al leer {extract_produits_tailles_path}: {e}")
    raise

try:
    head_swimming = pd.read_csv(head_swimming_path, delimiter=',', on_bad_lines='warn', encoding='latin1')
except pd.errors.ParserError as e:
    print(f"Error al leer {head_swimming_path}: {e}")
    raise

try:
    informe_maesarti = pd.read_csv(informe_maesarti_path, delimiter=',', on_bad_lines='warn', encoding='latin1')
except pd.errors.ParserError as e:
    print(f"Error al leer {informe_maesarti_path}: {e}")
    raise

try:
    stocks_spiuk = pd.read_csv(stocks_spiuk_path, delimiter=',', on_bad_lines='warn', encoding='latin1')
except pd.errors.ParserError as e:
    print(f"Error al leer {stocks_spiuk_path}: {e}")
    raise

try:
    stocks_myrco = pd.read_excel(stocks_myrco_path, sheet_name='Productos')
except Exception as e:
    print(f"Error al leer {stocks_myrco_path}: {e}")
    raise

try:
    availability = pd.read_csv(availability_path, delimiter=',', on_bad_lines='warn', encoding='latin1')
except pd.errors.ParserError as e:
    print(f"Error al leer {availability_path}: {e}")
    raise

try:
    stockssd = pd.read_csv(stockssd_path, delimiter=',', on_bad_lines='warn', encoding='latin1')
except pd.errors.ParserError as e:
    print(f"Error al leer {stockssd_path}: {e}")
    raise

try:
    hanker = pd.read_excel(hanker_path, sheet_name='Hanker')
except Exception as e:
    print(f"Error al leer {hanker_path}: {e}")
    raise

# Crear un diccionario para mapear códigos de barras a stocks de proveedores
proveedores = {
    'MARES': head_swimming.set_index('EAN')['QTY'].to_dict(),
    'BLUNAE': informe_maesarti.set_index('Código barras')['Stock físico'].to_dict(),
    'SPIUK': stocks_spiuk.set_index('--- EAN ---')['--- STOCK ---'].apply(lambda x: 6 if x == 'SI' else 0).to_dict(),
    'MYRCO': stocks_myrco.set_index('Ean')['Stock'].to_dict(),
    'SAILFISH': availability.set_index('Variant id')['instock'].to_dict(),
    'SOMOSDEPORTISTAS': stockssd.set_index('Código barras')['Stock almacén ALM'].to_dict(),
    'HANKER': hanker.set_index('CÓDIGO DE BARRAS')['STOCKPR'].to_dict()
}

# Actualizar el campo 'stock' con los datos de 'extract_produits_tailles.csv'
stock_auto['stock'] = stock_auto['codigo_barras'].map(extract_produits_tailles.set_index('Código de barras')['TRI FOR FUN, S.L.']).fillna(0)

# Actualizar el campo 'stock_proveedor' con los datos de los ficheros de proveedores
for proveedor, stock_dict in proveedores.items():
    stock_auto['stock_proveedor'] = stock_auto['codigo_barras'].map(stock_dict).fillna(stock_auto['stock_proveedor'])

# Guardar los cambios en 'stock_auto.csv'
stock_auto.to_csv(stock_auto_path, index=False)

print("Actualización completada.")

# Restaurar la salida estándar y de error
sys.stdout.close()
sys.stderr.close()
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__
