import os
import pandas as pd
fich1= 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/informe-maesarti.csv'
fich2= 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/actua_blunae.csv'


# Verifica si el fichero fich2.csv existe y, en caso afirmativo, lo borra
if os.path.exists(fich2):
    os.remove(fich2)

# Lee el fichero de entrada (fich1) con el carácter separador ";"
df = pd.read_csv(fich1, sep=';', encoding='utf-8')

# Selecciona las columnas 7 y 2
selected_columns = df.iloc[:, [7, 2]]

# Renombra las columnas
selected_columns.columns = ['codigo_barras', 'stock_proveedor']

# Guarda el resultado en un nuevo fichero (fich2 con las nuevas cabeceras en formato UTF-8
selected_columns.to_csv(fich2, index=False, sep=';', encoding='utf-8')





