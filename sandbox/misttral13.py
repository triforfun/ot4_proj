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

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# Comenta la siguiente línea para desactivar el modo headless
# chrome_options.add_argument("--headless")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "C:/Users/onlin/Downloads",
})

def download_report(driver, option_text, file_name):
    try:
        # Seleccionar opción del desplegable
        desplegable = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dropdown-toggle')]")))
        desplegable.click()

        opcion_hoka = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{option_text}')]")))
        opcion_hoka.click()

        # Enviar el formulario
        boton_enviar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enviar')]")))
        driver.execute_script("arguments[0].scrollIntoView();", boton_enviar)
        boton_enviar.click()

        # Esperar a que el archivo se descargue
        WebDriverWait(driver, 60).until(lambda d: os.path.exists(f"C:/Users/onlin/Downloads/{file_name}"))

        # Mover el archivo descargado a la carpeta deseada
        carpeta_descargas = "C:/Users/onlin/Downloads"
        carpeta_destino = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA"

        ruta_archivo_descargado = os.path.join(carpeta_descargas, file_name)
        ruta_archivo_destino = os.path.join(carpeta_destino, file_name)

        if os.path.exists(ruta_archivo_destino):
            nombre_sin_extension, extension = os.path.splitext(file_name)
            contador = 1
            while os.path.exists(os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")):
                contador += 1
            nuevo_nombre = f"{nombre_sin_extension} ({contador}){extension}"
            ruta_archivo_destino = os.path.join(carpeta_destino, nuevo_nombre)

        shutil.move(ruta_archivo_descargado, ruta_archivo_destino)
        print(f"Archivo movido a: {ruta_archivo_destino}")

    except Exception as e:
        print(f"Error al descargar el informe {option_text}:", e)

print("Comenzando el proceso")

# Configurar el driver automáticamente
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print("Driver configurado correctamente")
except Exception as e:
    print("Error al configurar el driver:", e)
    exit()

try:
    # Abrir la página de inicio de sesión
    driver.get("https://comercialudrab2b.elasticsuite.com/")
    print("Página de inicio de sesión abierta")

    # Iniciar sesión
    campo_usuario = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    campo_usuario.clear()
    campo_usuario.send_keys("info@triforfun.es")

    campo_password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
    campo_password.clear()
    campo_password.send_keys("HokaTff2022")
    campo_password.send_keys(Keys.RETURN)

    # Navegar al informe de inventario
    menu_gestiona = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Gestiona')]")))
    actions = ActionChains(driver)
    actions.move_to_element(menu_gestiona).perform()

    submenu_informe = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Informe de inventario')]")))
    submenu_informe.click()

    # Seleccionar y descargar el informe para HOKA SS25 Especialista
    download_report(driver, "HOKA SS25 Especialista", "HOKA SS25 Especialista.xlsx")

    # Seleccionar y descargar el informe para HOKA FW24 Especialista
    download_report(driver, "HOKA FW24 Especialista", "HOKA FW24 Especialista.xlsx")

except Exception as e:
    print("Ocurrió un error:", e)

finally:
    # Cerrar el navegador
    driver.quit()
