"""
exporta els fitxers de productes i variants a la carpeta stocks_externs
"""
import os
import time
import keyboard

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Maximizar la ventana del navegador
chrome_options.add_argument("--headless")  # Descomenta esta línea para ejecutar en modo headless


# Configura el driver automáticamente
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

print("Comença la exportacó dels fitxers de productes i variants de la web de Triforfun")


# carpeta y ficheros para borrar, mover
ruta_descarga = 'c:/Users/onlin/Downloads'
ruta_final = 'c:/TFF/DOCS/ONLINE/STOCKS_EXTERNS'
fich1 = 'extract_produits.csv'
fich2 = 'extract_produits_tailles.csv'
url="http://triforfun.hiboutik.com/"
path_driver=os.chdir('C:/Users/onlin/AppData/Local/Programs/Python/Python312/Scripts')

driver.get(url)
keyboard.press_and_release("tab")
time.sleep(2)

keyboard.press_and_release("tab")
time.sleep(2)

keyboard.press_and_release("tab")
time.sleep(2)

usuari = driver.find_element(By.NAME,"login_user")
usuari.send_keys("comercial@triforfun.es")

time.sleep(1)

psswrd = driver.find_element(By.NAME,"pass_user")
psswrd.send_keys("tffpsswrd")

entrar = driver.find_element(By.XPATH, "//button[@type='submit']")
entrar.click()

entrar2 = driver.find_element(By.XPATH, "/html/body/div[2]/nav/div/ul/li[4]/form")
entrar2.click()

# la linea siguiente no da error pero la de click si, debe ser por que no esta visualizado el submenu
entrar3 = driver.find_element(By.XPATH, "//li/ul/li/form/button[@type='submit'][@value='Importar-Exportar']")
entrar3.click()

entrar4 = driver.find_element(By.XPATH, "/html/body/div[2]/nav/div/ul/li[4]/ul/li[7]/form")
entrar4.click()

exportar_datos = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[1]/h4/a")
exportar_datos.click()

time.sleep(3)

generar_csv1 = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[7]/td[4]/form/button/span")
generar_csv1.click()

time.sleep(3)
descargar_csv1 = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[7]/td[5]/a/button/span")
descargar_csv1.click()

time.sleep(3)
# generar_csv2 = driver.find_element(By.XPATH,"/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[9]/td[4]/form")
generar_csv2 = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[9]/td[4]/form/button")
generar_csv2.click()
time.sleep(3)

descargar_csv2 = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[9]/td[5]/a/button/span")
descargar_csv2.click()

print("ha acabat la descarrega dels 2 fitxers")

time.sleep(10)  # espera 10 segons per a que es descarreguen els fitxers



driver.quit()
