"""
Descarga el stock disponible de Orca
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configura las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# Configura el driver automáticamente
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

url = "https://www.orbea.com/es-es/kide/acceso/"

try:
    driver.get(url)
    driver.maximize_window()  # Maximizar la ventana del navegador

    # Ingresar el nombre de usuario y contraseña
    usuari = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "login_email"))
    )
    usuari.send_keys("TRIFORFUN")
    print("Usuario ingresado")

    psswrd = driver.find_element(By.NAME, "login_password")
    psswrd.send_keys("kide183@")
    print("Contraseña ingresada")

    acceder = driver.find_element(By.XPATH, "//button[contains(text(), 'Acceder')]")
    acceder.click()
    print("Sesión iniciada")

    # Esperar a que la página cargue completamente después del inicio de sesión
    time.sleep(3)

    # Manejar el banner de cookies (ahora en el pie de página)
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", cookie_button)
        time.sleep(1)  # Esperar un momento para que la página se desplace
        cookie_button.click()
        print("Cookies aceptadas")
    except (NoSuchElementException, TimeoutException):
        print("No se encontró el botón de cookies o ya no es necesario")

    # Navegar a la sección de disponibilidad
    disponibilidad = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#heading > div.b2b-menu.visible > div.b2b-menu-options > div:nth-child(3) > ul > li:nth-child(3) > a"))
    )
    disponibilidad.click()
    print("Navegado a la sección de disponibilidad")

    # Esperar a que la página de disponibilidad cargue completamente
    time.sleep(3)

    # Localizar y hacer clic en el enlace "Exportar a CSV"
    exportar_csv = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#top > div > a:nth-child(2)"))
    )
    exportar_csv.click()
    print("Exportación a CSV iniciada")

    # Esperar a que la descarga se complete
    time.sleep(5)

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    driver.quit()
    print("Navegador cerrado")
