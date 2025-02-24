import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración
chrome_driver_path = "C:/Users/onlin/AppData/Local/Programs/Python/Python312/Scripts"
ruta_descarga = 'c:/Users/onlin/Downloads' 
ruta_final = 'c:/TFF/DOCS/ONLINE/STOCKS_EXTERNS'
archivo_productos = 'extract_produits.csv'
archivo_variantes = 'extract_produits_tailles.csv'
url = "http://triforfun.hiboutik.com/"

# Iniciar el driver
driver = webdriver.Chrome(executable_path=chrome_driver_path)
driver.get(url)

# Iniciar sesión (usando WebDriverWait como ejemplo)
try:
    # ... (código para iniciar sesión)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "login_user"))
    ).send_keys("comercial@triforfun.es") 
    # ... (resto del código para iniciar sesión)
except Exception as e:
    print(f"Error al iniciar sesión: {e}")

# ... (resto del código para exportar archivos)

# Mover archivos (usando os.path.join para construir rutas)
try:
    os.rename(os.path.join(ruta_descarga, archivo_productos), 
              os.path.join(ruta_final, archivo_productos))
    os.rename(os.path.join(ruta_descarga, archivo_variantes), 
              os.path.join(ruta_final, archivo_variantes))
except Exception as e:
    print(f"Error al mover los archivos: {e}")

driver.quit()