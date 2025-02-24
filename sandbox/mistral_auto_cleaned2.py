import pandas as pd
import os

# Ruta de los archivos
directory = r'C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS'
output_directory = r'C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\cleaned'
os.makedirs(output_directory, exist_ok=True)

# Función para leer y limpiar archivos CSV
def clean_csv(file_path, delimiter=';', encoding='ISO-8859-1'):
    try:
        # Leer el archivo CSV
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, on_bad_lines='warn')

        # Renombrar y reordenar columnas
        if 'Código de barras' in df.columns:
            df = df.rename(columns={'Código de barras': 'ean'})
        elif 'CÓDIGO DE BARRAS' in df.columns:
            df = df.rename(columns={'CÓDIGO DE BARRAS': 'ean'})
        elif 'EAN' in df.columns:
            df = df.rename(columns={'EAN': 'ean'})
        elif 'EAN ' in df.columns:
            df = df.rename(columns={'EAN ': 'ean'})
        elif 'CÃ³digo de barras' in df.columns:
            df = df.rename(columns={'CÃ³digo de barras': 'ean'})
        elif 'Código barras' in df.columns:
            df = df.rename(columns={'Código barras': 'ean'})
        elif '--- EAN ---' in df.columns:
            df = df.rename(columns={'--- EAN ---': 'ean'})
        elif 'Variant Id' in df.columns:
            df = df.rename(columns={'Variant Id': 'ean'})

        if 'TRI FOR FUN, S.L.' in df.columns:
            df = df.rename(columns={'TRI FOR FUN, S.L.': 'qty'})
        elif 'QTY' in df.columns:
            df = df.rename(columns={'QTY': 'qty'})
        elif 'Stock físico' in df.columns:
            df = df.rename(columns={'Stock físico': 'qty'})
        elif 'Stock' in df.columns:
            df = df.rename(columns={'Stock': 'qty'})
        elif '--- STOCK ---' in df.columns:
            df = df.rename(columns={'--- STOCK ---': 'qty'})
        elif 'Instock' in df.columns:
            df = df.rename(columns={'Instock': 'qty'})

        # Limpiar y convertir las columnas 'ean' y 'qty' a enteros
        if 'ean' in df.columns:
            df['ean'] = df['ean'].replace({',': ''}, regex=True).fillna(0).astype(float).astype(int)
        if 'qty' in df.columns:
            df['qty'] = df['qty'].replace({',': ''}, regex=True).replace({'SI': 1, 'NO': 0}, regex=True).fillna(0).astype(float).astype(int)
            df['qty'] = df['qty'].infer_objects(copy=False)  # Abordar FutureWarning

        # Reordenar columnas para que 'ean' y 'qty' estén al principio
        if 'ean' in df.columns and 'qty' in df.columns:
            cols = ['ean', 'qty'] + [col for col in df if col not in ['ean', 'qty']]
            df = df[cols]

        # Guardar el archivo limpio
        output_path = os.path.join(output_directory, os.path.basename(file_path))
        df.to_csv(output_path, index=False, sep=';', encoding='utf-8')
        print(f"Cleaned file saved to {output_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Lista de archivos a procesar
files_to_clean = [
    'extract_produits_tailles.csv',
    'head_Swimming_infostock.txt.csv',
    'informe-maesarti.csv',
    'stocks-spiuk.csv',
    'Availability.csv',
    'STOCKSSD.CSV'
]

# Procesar cada archivo
for file_name in files_to_clean:
    file_path = os.path.join(directory, file_name)
    clean_csv(file_path)