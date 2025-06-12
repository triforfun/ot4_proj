"""
Descarga los archivos .csv de Sailfish y Blunae.
"""
import requests
from pathlib import Path
import time

# URLs de los archivos a descargar
URL_SAILFISH = "https://feed.mulwi.com/f/sailfish-b2b/custom.csv"
URL_BLUNAE = "http://descargas.blunae.es/informe-maesarti.csv"

# Ruta donde se guardarán los archivos
DOWNLOAD_PATH = Path('C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/')

def download_file(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la solicitud falla
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Archivo descargado exitosamente desde {url}.")
    except requests.RequestException as e:
        print(f"Error al descargar el archivo desde {url}: {e}")

def main():
    # Asegurarse de que el directorio de descarga exista
    DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)

    # Descargar el archivo de Sailfish
    print("Descargando archivo de Sailfish...")
    sailfish_file_path = DOWNLOAD_PATH / 'Availability.csv'
    download_file(URL_SAILFISH, sailfish_file_path)

    # Descargar el archivo de Blunae
    print("Descargando archivo de Blunae...")
    blunae_file_path = DOWNLOAD_PATH / 'informe-maesarti.csv'
    download_file(URL_BLUNAE, blunae_file_path)

    print("Todas las descargas se han completado con éxito.")

if __name__ == "__main__":
    main()
