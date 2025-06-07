from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import os
import shutil
import time

# Configuración de Chrome para usar un perfil de usuario existente
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--user-data-dir=C:/Users/onlin/AppData/Local/Google/Chrome/User Data")  # Ruta al directorio de datos de usuario de Chrome
chrome_options.add_argument("--profile-directory=TffDrive")  # Nombre del perfil que deseas usar

# Configuración del directorio de descarga
download_path = "C:/Users/onlin/Downloads"
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

def wait_for_file(download_path, file_name, timeout=10):
    """Espera a que el archivo aparezca en el directorio de descargas"""
    file_path = os.path.join(download_path, file_name)
    end_time = time.time() + timeout
    while time.time() < end_time:
        if os.path.exists(file_path):
            return True
        time.sleep(1)
    return False

def main():
    print("Iniciando proceso de descarga...")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Driver configurado")
    except Exception as e:
        print(f"Error configurando driver: {e}")
        return

    try:
        driver.get("https://comercialudrab2b.elasticsuite.com/")
        print("Página abierta")
        time.sleep(3)

        # Aquí puedes continuar con el resto de tu lógica de automatización

    except Exception as e:
        print(f"Error general: {str(e)}")
    finally:
        try:
            driver.quit()
            print("Navegador cerrado")
        except Exception as e:
            print(f"Error al cerrar el navegador: {e}")

if __name__ == "__main__":
    main()
