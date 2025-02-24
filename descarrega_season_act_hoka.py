"""
codi per baixar-se el inventari de hoka a la season actual
"""
# pylint: disable=invalid-name

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import os
import shutil

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Maximizar la ventana del navegador
chrome_options.add_argument("--headless")  # Descomenta esta línea para ejecutar en modo headless

print ("comença el procés")

# Configurar el driver automáticamente

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Abrir la página de inicio de sesión
    driver.get("https://comercialudrab2b.elasticsuite.com/")

    # Esperar a que la página cargue completamente
    wait = WebDriverWait(driver, 10)  # Esperar hasta 10 segundos

    # Iniciar sesión (código anterior)
    campo_usuario = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    campo_usuario.clear()
    campo_usuario.send_keys("info@triforfun.es")

    campo_password = wait.until(EC.presence_of_element_located((By.NAME, "password")))
    campo_password.clear()
    campo_password.send_keys("HokaTff2022")

    campo_password.send_keys(Keys.RETURN)

    # Esperar a que la página de inicio cargue después del login
    time.sleep(5)  # Ajusta este tiempo según sea necesario

    # Localizar el menú "Gestiona" usando XPath
    menu_gestiona = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@content='Gestiona']")))

    # Simular el movimiento del ratón sobre el menú "Gestiona"
    actions = ActionChains(driver)
    actions.move_to_element(menu_gestiona).perform()

    # Esperar a que el submenú aparezca
    time.sleep(2)  # Ajusta este tiempo según sea necesario

    # Localizar la opción "Informe de inventario" usando XPath
    submenu_informe = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Informe de inventario')]")))

    # Hacer clic en la opción "Informe de inventario"
    submenu_informe.click()

    # Esperar a que la página de "Informe de inventario" cargue
    time.sleep(5)

    # Localizar el desplegable usando XPath
    desplegable = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[12]/div[2]/div/div[2]/div[2]/div[2]/div/div/div/form/div[2]/div[2]/div/div/div[1]")))

    # Hacer clic en el desplegable para abrir las opciones
    desplegable.click()

    # Esperar a que las opciones del desplegable aparezcan
    time.sleep(2)

    # Localizar la opción "HOKA SS25 Especialista" usando XPath
    opcion_hoka = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'HOKA SS25 Especialista')]")))

    # Hacer clic en la opción "HOKA SS25 Especialista"
    opcion_hoka.click()

    # Esperar a que la selección se fije
    time.sleep(2)

    # Cerrar el menú desplegable haciendo clic fuera de él
    driver.find_element(By.TAG_NAME, "body").click()

    # Esperar a que el menú se cierre
    time.sleep(2)

    # Localizar el botón "Enviar" usando el XPath proporcionado
    boton_enviar = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[12]/div[2]/div/div[2]/div[2]/div[2]/div/div/div/form/div[4]/button")))

    # Desplazar la página hasta el botón "Enviar"
    driver.execute_script("arguments[0].scrollIntoView();", boton_enviar)

    # Esperar a que el botón esté visible y habilitado
    wait.until(EC.visibility_of(boton_enviar))
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[12]/div[2]/div/div[2]/div[2]/div[2]/div/div/div/form/div[4]/button")))

    # Hacer clic en el botón "Enviar" usando JavaScript
    driver.execute_script("arguments[0].click();", boton_enviar)

    # Esperar a que el archivo se descargue completamente
    time.sleep(10)  # Ajusta este tiempo según sea necesario

    #aqui acaba la descarrega de la season actual de HOKA
    # canviar els noms de la season quan correspongui
    #aqui comença la descarrega de la season anterior de HOKA
    # Localizar el desplegable usando XPath
    desplegable = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[12]/div[2]/div/div[2]/div[2]/div[2]/div/div/div/form/div[2]/div[2]/div/div/div[1]")))

    # Hacer clic en el desplegable para abrir las opciones
    desplegable.click()

    # Esperar a que las opciones del desplegable aparezcan
    time.sleep(2)

    # Localizar la opción "HOKA FW24 Especialista" usando XPath
    opcion_hoka = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'HOKA FW24 Especialista')]")))

    # Hacer clic en la opción "HOKA FW24 Especialista"
    opcion_hoka.click()

    # Esperar a que la selección se fije
    time.sleep(2)

    # Cerrar el menú desplegable haciendo clic fuera de él
    driver.find_element(By.TAG_NAME, "body").click()

    # Esperar a que el menú se cierre
    time.sleep(2)

    # Localizar el botón "Enviar" usando el XPath proporcionado
    boton_enviar = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[12]/div[2]/div/div[2]/div[2]/div[2]/div/div/div/form/div[4]/button")))

    # Desplazar la página hasta el botón "Enviar"
    driver.execute_script("arguments[0].scrollIntoView();", boton_enviar)

    # Esperar a que el botón esté visible y habilitado
    wait.until(EC.visibility_of(boton_enviar))
    wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[12]/div[2]/div/div[2]/div[2]/div[2]/div/div/div/form/div[4]/button")))

    # Hacer clic en el botón "Enviar" usando JavaScript
    driver.execute_script("arguments[0].click();", boton_enviar)

    # Esperar a que el archivo se descargue completamente
    time.sleep(10)  # Ajusta este tiempo según sea necesario


    #aqui acaba la descarrega de la season anterior de HOKA


    # Mover el archivo descargado DE LA SEASON ACTUAL a la carpeta deseada
    carpeta_descargas = "C:/Users/onlin/Downloads"
    carpeta_destino = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA"
    nombre_archivo = "HOKA SS25 Especialista.xlsx"

    # Ruta completa del archivo descargado
    ruta_archivo_descargado = os.path.join(carpeta_descargas, nombre_archivo)

    # Verificar si el archivo ya existe en la carpeta de destino
    if os.path.exists(os.path.join(carpeta_destino, nombre_archivo)):
        # Si existe, renombrar el archivo descargado
        nombre_sin_extension, extension = os.path.splitext(nombre_archivo)
        contador = 1
        while os.path.exists(os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")):
            contador += 1
        nuevo_nombre = f"{nombre_sin_extension} ({contador}){extension}"
        ruta_archivo_destino = os.path.join(carpeta_destino, nuevo_nombre)
    else:
        ruta_archivo_destino = os.path.join(carpeta_destino, nombre_archivo)

    # Mover el archivo a la carpeta de destino
    shutil.move(ruta_archivo_descargado, ruta_archivo_destino)

    print(f"Archivo movido a: {ruta_archivo_destino}")


    # Mover el archivo descargado DE LA SEASON ANTERIOR a la carpeta deseada
    carpeta_descargas = "C:/Users/onlin/Downloads"
    carpeta_destino = "C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA"
    nombre_archivo = "HOKA FW24 Especialista.xlsx"

    # Ruta completa del archivo descargado
    ruta_archivo_descargado = os.path.join(carpeta_descargas, nombre_archivo)

    # Verificar si el archivo ya existe en la carpeta de destino
    if os.path.exists(os.path.join(carpeta_destino, nombre_archivo)):
        # Si existe, renombrar el archivo descargado
        nombre_sin_extension, extension = os.path.splitext(nombre_archivo)
        contador = 1
        while os.path.exists(os.path.join(carpeta_destino, f"{nombre_sin_extension} ({contador}){extension}")):
            contador += 1
        nuevo_nombre = f"{nombre_sin_extension} ({contador}){extension}"
        ruta_archivo_destino = os.path.join(carpeta_destino, nuevo_nombre)
    else:
        ruta_archivo_destino = os.path.join(carpeta_destino, nombre_archivo)

    # Mover el archivo a la carpeta de destino
    shutil.move(ruta_archivo_descargado, ruta_archivo_destino)

    print(f"Archivo movido a: {ruta_archivo_destino}")

except Exception as e:
    print("Ocurrió un error:", e)

finally:
    # Cerrar el navegador
    driver.quit()