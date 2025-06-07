from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, NoSuchElementException
import os
import shutil
import time
import glob

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Configurar directorio de descarga
download_path = "C:/Users/onlin/Downloads"
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

def wait_for_download(download_path, timeout=60):
    """Espera a que termine la descarga verificando archivos .crdownload"""
    end_time = time.time() + timeout
    while time.time() < end_time:
        downloading_files = glob.glob(os.path.join(download_path, "*.crdownload"))
        if not downloading_files:
            time.sleep(1)
            return True
        time.sleep(1)
    return False

def find_latest_excel_file(download_path):
    """Encuentra el archivo Excel más reciente en el directorio de descargas"""
    excel_files = glob.glob(os.path.join(download_path, "*.xlsx"))
    if not excel_files:
        excel_files = glob.glob(os.path.join(download_path, "*.xls"))

    if excel_files:
        latest_file = max(excel_files, key=os.path.getmtime)
        return latest_file
    return None

def click_catalog_dropdown(driver):
    """Hacer clic en el desplegable de catálogo usando múltiples estrategias"""
    strategies = [
        # Estrategia 1: Buscar por texto "ARENA SS25"
        lambda: driver.find_element(By.XPATH, "//*[contains(text(), 'ARENA SS25')]"),

        # Estrategia 2: Buscar elementos con flecha hacia abajo (▼)
        lambda: driver.find_element(By.XPATH, "//div[contains(text(), 'ARENA SS25')]/following-sibling::*[contains(@class, 'arrow') or contains(text(), '▼')]"),

        # Estrategia 3: Buscar el contenedor padre
        lambda: driver.find_element(By.XPATH, "//*[contains(text(), 'ARENA SS25')]/parent::*"),

        # Estrategia 4: Buscar por Bootstrap dropdown
        lambda: driver.find_element(By.XPATH, "//div[contains(@class, 'dropdown') and contains(., 'ARENA SS25')]"),

        # Estrategia 5: Buscar input o select
        lambda: driver.find_element(By.XPATH, "//input[contains(@value, 'ARENA')] | //select[contains(., 'ARENA')]"),
    ]

    for i, strategy in enumerate(strategies):
        try:
            print(f"Probando estrategia {i+1} para encontrar desplegable...")
            element = strategy()
            if element.is_displayed() and element.is_enabled():
                print(f"✓ Estrategia {i+1} exitosa")

                # Intentar hacer clic
                try:
                    element.click()
                    return True
                except:
                    # Si el clic directo falla, usar JavaScript
                    driver.execute_script("arguments[0].click();", element)
                    return True

        except Exception as e:
            print(f"✗ Estrategia {i+1} falló: {str(e)[:100]}")
            continue

    return False

def select_catalog_option(driver, option_text):
    """Seleccionar una opción específica del catálogo"""
    print(f"Buscando opción: {option_text}")

    # Esperar un poco para que aparezcan las opciones
    time.sleep(2)

    option_strategies = [
        # Estrategia 1: Buscar directamente por texto
        lambda: driver.find_element(By.XPATH, f"//*[contains(text(), '{option_text}')]"),

        # Estrategia 2: Buscar en elementos de lista
        lambda: driver.find_element(By.XPATH, f"//li[contains(text(), '{option_text}')]"),

        # Estrategia 3: Buscar en opciones de select
        lambda: driver.find_element(By.XPATH, f"//option[contains(text(), '{option_text}')]"),

        # Estrategia 4: Buscar en divs clickables
        lambda: driver.find_element(By.XPATH, f"//div[@role='option' and contains(text(), '{option_text}')]"),

        # Estrategia 5: Buscar parcialmente por "HOKA"
        lambda: driver.find_element(By.XPATH, f"//*[contains(text(), 'HOKA') and contains(text(), 'Especialista')]"),
    ]

    for i, strategy in enumerate(option_strategies):
        try:
            print(f"Probando estrategia {i+1} para encontrar opción...")
            element = strategy()
            if element.is_displayed():
                print(f"✓ Opción encontrada con estrategia {i+1}")

                # Scroll hacia el elemento
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)

                # Intentar hacer clic
                try:
                    element.click()
                    return True
                except:
                    driver.execute_script("arguments[0].click();", element)
                    return True

        except Exception as e:
            print(f"✗ Estrategia {i+1} falló: {str(e)[:100]}")
            continue

    return False

def click_submit_button(driver):
    """Hacer clic en el botón Enviar"""
    print("Buscando botón Enviar...")

    button_strategies = [
        lambda: driver.find_element(By.XPATH, "//button[contains(text(), 'Enviar')]"),
        lambda: driver.find_element(By.XPATH, "//input[@value='Enviar']"),
        lambda: driver.find_element(By.XPATH, "//button[@type='submit']"),
        lambda: driver.find_element(By.XPATH, "//*[contains(@class, 'btn') and contains(text(), 'Enviar')]"),
        lambda: driver.find_element(By.XPATH, "//button[contains(@class, 'btn-primary')]"),
    ]

    for i, strategy in enumerate(button_strategies):
        try:
            print(f"Probando estrategia {i+1} para encontrar botón...")
            button = strategy()
            if button.is_displayed() and button.is_enabled():
                print(f"✓ Botón encontrado con estrategia {i+1}")

                # Scroll hacia el botón
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)

                # Hacer clic
                try:
                    button.click()
                    return True
                except:
                    driver.execute_script("arguments[0].click();", button)
                    return True

        except Exception as e:
            print(f"✗ Estrategia {i+1} falló: {str(e)[:100]}")
            continue

    return False

def download_report_simple(driver, catalog_option, expected_file_name):
    """Versión simplificada del proceso de descarga"""
    try:
        print(f"\n=== Descargando: {catalog_option} ===")

        # Paso 1: Hacer clic en el desplegable de catálogo
        if not click_catalog_dropdown(driver):
            print("❌ No se pudo abrir el desplegable de catálogo")
            return False

        print("✓ Desplegable de catálogo abierto")
        time.sleep(2)

        # Paso 2: Seleccionar la opción
        if not select_catalog_option(driver, catalog_option):
            print(f"❌ No se pudo seleccionar la opción: {catalog_option}")
            return False

        print(f"✓ Opción seleccionada: {catalog_option}")
        time.sleep(2)

        # Paso 3: Hacer clic en Enviar
        if not click_submit_button(driver):
            print("❌ No se pudo hacer clic en el botón Enviar")
            return False

        print("✓ Botón Enviar presionado")

        # Paso 4: Esperar descarga
        print("Esperando descarga...")
        if wait_for_download(download_path, timeout=120):
            latest_file = find_latest_excel_file(download_path)
            if latest_file:
                # Mover archivo
                carpeta_destino = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA"
                os.makedirs(carpeta_destino, exist_ok=True)

                nombre_sin_extension, extension = os.path.splitext(expected_file_name)
                ruta_archivo_destino = os.path.join(carpeta_destino, expected_file_name)

                if os.path.exists(ruta_archivo_destino):
                    contador = 1
                    while os.path.exists(os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")):
                        contador += 1
                    ruta_archivo_destino = os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")

                shutil.move(latest_file, ruta_archivo_destino)
                print(f"✅ Archivo descargado y movido a: {ruta_archivo_destino}")
                return True
            else:
                print("❌ No se encontró archivo descargado")
                return False
        else:
            print("❌ Timeout esperando descarga")
            return False

    except Exception as e:
        print(f"❌ Error en descarga: {str(e)}")
        return False

def main():
    print("🚀 Iniciando proceso de descarga...")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print("✓ Driver configurado")
    except Exception as e:
        print(f"❌ Error configurando driver: {e}")
        return

    try:
        # Login
        driver.get("https://comercialudrab2b.elasticsuite.com/")
        print("✓ Página abierta")
        time.sleep(3)

        campo_usuario = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        campo_usuario.send_keys("info@triforfun.es")

        campo_password = driver.find_element(By.NAME, "password")
        campo_password.send_keys("HokaTff2022")
        campo_password.send_keys(Keys.RETURN)
        print("✓ Login enviado")
        time.sleep(5)

        # Navegar a inventario
        menu_gestiona = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Gestiona')]"))
        )
        ActionChains(driver).move_to_element(menu_gestiona).perform()
        time.sleep(2)

        submenu_informe = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Informe de inventario')]"))
        )
        submenu_informe.click()
        print("✓ Navegación exitosa")
        time.sleep(3)

        # Descargar reportes
        reportes = [
            ("HOKA SS25 Especialista", "HOKA_SS25_Especialista.xlsx"),
            ("HOKA FW24 Especialista", "HOKA_FW24_Especialista.xlsx")
        ]

        successful_downloads = 0
        for catalog_option, file_name in reportes:
            if download_report_simple(driver, catalog_option, file_name):
                successful_downloads += 1
            time.sleep(5)  # Esperar entre descargas

        print(f"\n🎯 Proceso completado: {successful_downloads}/{len(reportes)} descargas exitosas")

    except Exception as e:
        print(f"❌ Error general: {str(e)}")
    finally:
        try:
            driver.quit()
            print("✓ Navegador cerrado")
        except:
            pass

if __name__ == "__main__":
    main()