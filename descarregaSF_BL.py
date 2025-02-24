"""
Descarga los archivos .csv de Sailfish y Blunae
"""
import requests
import os
import time

# URLs de los archivos a descargar
url_sailfish = "https://feed.mulwi.com/f/sailfish-b2b/custom.csv"
url_blunae = "http://descargas.blunae.es/informe-maesarti.csv"

# Ruta donde se guardarán los archivos
download_path = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/'

# Asegurarse de que el directorio de descarga exista
os.makedirs(download_path, exist_ok=True)

# Descargar el archivo de Sailfish
print("Descargando archivo de Sailfish...")
response_sailfish = requests.get(url_sailfish)
with open(os.path.join(download_path, 'Availability.csv'), 'wb') as file:
    file.write(response_sailfish.content)
print("Archivo de Sailfish descargado.")

# Esperar un momento antes de la siguiente descarga
time.sleep(5)

# Descargar el archivo de Blunae
print("Descargando archivo de Blunae...")
response_blunae = requests.get(url_blunae)
with open(os.path.join(download_path, 'informe-maesarti.csv'), 'wb') as file:
    file.write(response_blunae.content)
print("Archivo de Blunae descargado.")
