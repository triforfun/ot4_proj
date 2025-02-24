"""
es baixa l'stock de la web de SPIUK
"""
import os
# debug import shutil
import time
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


url="https://www.spiuk.pro/es/"
# path_driver=os.chdir('C:/Users/onlin/AppData/Local/Programs/Python/Python311/Scripts')

print("comença la descarrega de SPIUK")

driver.get(url)

delegacion = driver.find_element(By.NAME,"Delegacion")
delegacion.send_keys("5962")

time.sleep(1)

Clave = driver.find_element(By.NAME,"Clave")
Clave.send_keys("03130524")

acceder = driver.find_element(By.XPATH, "/html/body/main/div/div/form/div[3]/button")
acceder.click()

time.sleep(10)

descargas = driver.find_element(By.XPATH, "/html/body/header/div[1]/nav/div/ul/li[3]/a")
descargas.click()

time.sleep(3)

stock_csv = driver.find_element(By.XPATH, "/html/body/header/div[1]/nav/div/ul/li[3]/ul/li[1]/a")
stock_csv.click()


time.sleep(1)

print("acabó descarga de SPIUK")

driver.quit()