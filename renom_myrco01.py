import os
import time

# Ruta de la carpeta donde se guardan los archivos
carpeta = r'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS'

# Nombre fijo que deseas para el archivo
nombre_fijo = 'Stock Myrco Sport.xlsx'

def renombrar_archivo():
    # Listar todos los archivos en la carpeta
    archivos = os.listdir(carpeta)

    # Filtrar archivos .xlsx
    archivos_xlsx = [archivo for archivo in archivos if archivo.endswith('.xlsx')]

    if archivos_xlsx:
        # Tomar el archivo más reciente
        archivo_mas_reciente = max(archivos_xlsx, key=lambda x: os.path.getctime(os.path.join(carpeta, x)))

        # Ruta completa del archivo más reciente
        ruta_archivo_mas_reciente = os.path.join(carpeta, archivo_mas_reciente)

        # Ruta completa del archivo con el nombre fijo
        ruta_archivo_fijo = os.path.join(carpeta, nombre_fijo)

        # Renombrar el archivo
        os.rename(ruta_archivo_mas_reciente, ruta_archivo_fijo)
        print(f'Archivo renombrado a {nombre_fijo}')
    else:
        print('No se encontraron archivos .xlsx en la carpeta')

# Ejecutar la función cada cierto intervalo de tiempo
while True:
    renombrar_archivo()
    time.sleep(3600)  # Esperar 1 hora antes de volver a comprobar
