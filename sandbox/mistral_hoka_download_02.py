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

# Configuración de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Configuración del directorio de descarga
download_path = "C:/Users/onlin/Downloads"
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

def wait_for_file(download_path, file_name, timeout=30):
    """Espera a que el archivo aparezca en el directorio de descargas"""
    file_path = os.path.join(download_path, file_name)
    end_time = time.time() + timeout
    while time.time() < end_time:
        if os.path.exists(file_path):
            return True
        time.sleep(1)
    return False

def click_catalog_dropdown(driver):
    """Hacer clic en el desplegable de catálogo"""
    try:
        element = driver.find_element(By.XPATH, "//*[contains(text(), 'ARENA SS25')]")
        if element.is_displayed() and element.is_enabled():
            element.click()
            return True
    except Exception as e:
        print(f"Error al hacer clic en el desplegable: {e}")
    return False

def select_catalog_option(driver, option_text):
    """Seleccionar una opción específica del catálogo"""
    try:
        element = driver.find_element(By.XPATH, f"//*[contains(text(), '{option_text}')]")
        if element.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.click()
            return True
    except Exception as e:
        print(f"Error al seleccionar la opción: {e}")
    return False

def click_submit_button(driver):
    """Hacer clic en el botón Enviar"""
    try:
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Enviar')]")
        if button.is_displayed() and button.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            button.click()
            return True
    except Exception as e:
        print(f"Error al hacer clic en el botón Enviar: {e}")
    return False

def download_report_simple(driver, catalog_option, expected_file_name):
    """Proceso simplificado de descarga"""
    try:
        print(f"\n=== Descargando: {catalog_option} ===")

        if not click_catalog_dropdown(driver):
            print("No se pudo abrir el desplegable de catálogo")
            return False

        print("Desplegable de catálogo abierto")
        time.sleep(2)

        if not select_catalog_option(driver, catalog_option):
            print(f"No se pudo seleccionar la opción: {catalog_option}")
            return False

        print(f"Opción seleccionada: {catalog_option}")
        time.sleep(2)

        if not click_submit_button(driver):
            print("No se pudo hacer clic en el botón Enviar")
            return False

        print("Botón Enviar presionado")

        print("Esperando descarga...")
        if wait_for_file(download_path, expected_file_name, timeout=10):
            carpeta_destino = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA"
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta_archivo_descargado = os.path.join(download_path, expected_file_name)
            ruta_archivo_destino = os.path.join(carpeta_destino, expected_file_name)

            if os.path.exists(ruta_archivo_destino):
                nombre_sin_extension, extension = os.path.splitext(expected_file_name)
                contador = 1
                while os.path.exists(os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")):
                    contador += 1
                ruta_archivo_destino = os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")

            shutil.move(ruta_archivo_descargado, ruta_archivo_destino)
            print(f"Archivo descargado y movido a: {ruta_archivo_destino}")
            return True
        else:
            print("Timeout esperando descarga")
            return False

    except Exception as e:
        print(f"Error en descarga: {str(e)}")
        return False

def main():
    print("Iniciando proceso de descarga...")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("Driver configurado")
    except Exception as e:
        print(f"Error configurando driver: {e}")
        return

    try:
        driver.get("https://comercialudrab2b.elasticsuite.com/")
        print("Página abierta")
        time.sleep(3)

        campo_usuario = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        campo_usuario.send_keys("info@triforfun.es")

        campo_password = driver.find_element(By.NAME, "password")
        campo_password.send_keys("HokaTff2022")
        campo_password.send_keys(Keys.RETURN)
        print("Login enviado")
        time.sleep(5)

        menu_gestiona = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Gestiona')]"))
        )
        ActionChains(driver).move_to_element(menu_gestiona).perform()
        time.sleep(2)

        submenu_informe = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Informe de inventario')]"))
        )
        submenu_informe.click()
        print("Navegación exitosa")
        time.sleep(3)

        reportes = [
            ("HOKA SS25 Especialista", "HOKA_SS25_Especialista.xlsx"),
            ("HOKA FW24 Especialista", "HOKA_FW24_Especialista.xlsx")
        ]

        successful_downloads = 0
        for catalog_option, file_name in reportes:
            if download_report_simple(driver, catalog_option, file_name):
                successful_downloads += 1
            time.sleep(5)
            driver.refresh()
            time.sleep(3)

        print(f"\nProceso completado: {successful_downloads}/{len(reportes)} descargas exitosas")

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
