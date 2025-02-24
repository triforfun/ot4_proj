import os
# debug import shutil
import time
# debug import selenium
# debug import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from sandbox import maq

# debug from selenium.webdriver.chrome.service import Service
# debug from selenium.webdriver.common.keys import Keys
# debug from selenium.webdriver.support.ui import WebDriverWait
# debug from selenium.webdriver.support import expected_conditions as EC
# debug from selenium.webdriver.common.action_chains import ActionChains
# debug from selenium.common.exceptions import NoSuchElementException, TimeoutException

# from selenium.webdriver.chrome.service import Service as ChromeService
# debug from webdriver_manager.chrome import ChromeDriverManager


driver = webdriver.Chrome()

url="https://www.orbea.com/es-es/kide/acceso/"
path_driver=os.chdir('C:/Users/onlin/AppData/Local/Programs/Python/Python312/Scripts')                   
                   
# driver.minimize_window()
chrome_options = Options()

driver.get(url)

time.sleep(4)

cookies = driver.find_element(By.XPATH,"/html/body/div[7]/div[3]/div/div[1]/div/div[2]/div/button[3]")

cookies.click()


print("paso por cookies")

usuari = driver.find_element(By.NAME,"login_email")
usuari.send_keys("TRIFORFUN")

time.sleep(1)
print("paso por usuari")

psswrd = driver.find_element(By.NAME,"login_password")
psswrd.send_keys("kide183@")

acceder = driver.find_element(By.XPATH, "/html/body/div[1]/div[8]/div/form/p[2]/button")
acceder.click()

disponibilidad = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div[1]/div[3]/ul/li[3]/a")
disponibilidad.click()

time.sleep(3)

descarga_csv = driver.find_element(By.XPATH,"/html/body/div[1]/div[7]/div[1]/div/header/div/a[2]")
descarga_csv.click()

print("acabo")

# url2 ="https://www.orbea.com/es-es/kide/available/csv/"
# driver.get(url2)
time.sleep(1)

driver.quit()