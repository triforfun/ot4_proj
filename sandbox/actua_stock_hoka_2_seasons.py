"""
Script para actualizar el stock_proveedor en el archivo productes_hokacatalogo.csv
usando los datos de los archivos HOKA SS25 Especialista.xlsx y HOKA FW24 Especialista.xlsx.
Si una referencia no está en ninguno de los Excel, se establece stock_proveedor a 0.
Finalmente, se copia el archivo CSV actualizado a la carpeta c:/pujaftp.
"""

import pandas as pd
import os
import shutil

# Rutas de los archivos
ruta_excel_ss25 = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA/HOKA SS25 Especialista.xlsx"
ruta_excel_fw24 = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA/HOKA FW24 Especialista.xlsx"
ruta_csv = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA/productes_hokacatalogo.csv"
ruta_copia_csv = "c:/pujaftp/puja_hokacatalogo.csv"

try:
    # Leer los archivos Excel
    df_excel_ss25 = pd.read_excel(ruta_excel_ss25)
    df_excel_fw24 = pd.read_excel(ruta_excel_fw24)

    # Combinar los datos de stock de ambos archivos Excel
    stock_dict_ss25 = df_excel_ss25.set_index('SKU')['Quantity Available'].to_dict()
    stock_dict_fw24 = df_excel_fw24.set_index('SKU')['Quantity Available'].to_dict()

    # Combinar los diccionarios, dando prioridad a SS25 en caso de duplicados
    stock_dict = {**stock_dict_fw24, **stock_dict_ss25}

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