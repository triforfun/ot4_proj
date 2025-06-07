"""
Script para actualizar el stock_proveedor en el archivo productes_hokacatalogo.csv
usando los datos de los archivos HOKA SS25 Especialista.xlsx y HOKA FW24 Especialista.xlsx.
Si una referencia no está en ninguno de los Excel, o si las fechas Available Date o Retail Date
son posteriores a la fecha actual, se establece stock_proveedor a 0.
Finalmente, se copia el archivo CSV actualizado a la carpeta c:/pujaftp.
"""

import pandas as pd
import os
import shutil
from datetime import datetime

# Rutas de los archivos
ruta_excel_ss25 = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA/HOKA SS25 Especialista.xlsx"
ruta_excel_fw24 = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA/HOKA FW24 Especialista.xlsx"
ruta_csv = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA/productes_hokacatalogo.csv"
ruta_copia_csv = "c:/pujaftp/puja_hokacatalogo.csv"

# Obtener la fecha actual
fecha_actual = datetime.now()

try:
    # Leer los archivos Excel
    df_excel_ss25 = pd.read_excel(ruta_excel_ss25)
    df_excel_fw24 = pd.read_excel(ruta_excel_fw24)

    # Combinar los datos de ambos archivos Excel
    df_excel_combined = pd.concat([df_excel_ss25, df_excel_fw24])

    # Filtrar los datos según las fechas Available Date y Retail Date
    df_excel_filtered = df_excel_combined[
        (pd.to_datetime(df_excel_combined['Available Date'], errors='coerce') <= fecha_actual) &
        (pd.to_datetime(df_excel_combined['Retail Date'], errors='coerce') <= fecha_actual)
    ]

    # Crear un diccionario con las referencias y cantidades disponibles filtradas
    stock_dict = df_excel_filtered.set_index('SKU')['Quantity Available'].to_dict()

    # Leer el archivo CSV
    df_csv = pd.read_csv(ruta_csv, delimiter=';')  # Ajusta el delimitador si es necesario

    # Actualizar el campo stock_proveedor en el CSV
    df_csv['stock_proveedor'] = df_csv['referencia'].map(stock_dict).fillna(0).astype(int)

    # Guardar el archivo CSV actualizado
    df_csv.to_csv(ruta_csv, index=False, sep=';')  # Ajusta el delimitador si es necesario

    # Mover una copia del archivo CSV a c:/pujaftp
    shutil.copy(ruta_csv, ruta_copia_csv)

    print("Archivo CSV actualizado y copiado correctamente.")

except Exception as e:
    print("Ocurrió un error:", e)