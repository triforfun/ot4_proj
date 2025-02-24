"""
fitxer per exportar els fitxer de productes i de variants
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def setup_driver():
    driver = webdriver.Chrome()
    driver.get("http://triforfun.hiboutik.com/")
    return driver

def login(driver, username, password):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
    except TimeoutException as e:
        print(f"Error during login: TimeoutException: {e}")
    except NoSuchElementException as e:
        print(f"Error during login: NoSuchElementException: {e}")

def navigate_to_export_page(driver):
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/nav/div/ul/li[4]/form"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//li/ul/li/form/button[@type='submit'][@value='Importar-Exportar']"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/nav/div/ul/li[4]/ul/li[7]/form"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[1]/h4/a"))).click()
    except TimeoutException as e:
        print(f"Error navigating to export page: TimeoutException: {e}")
    except NoSuchElementException as e:
        print(f"Error navigating to export page: NoSuchElementException: {e}")

def export_csv(driver, row):
    try:
        generar_csv = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[{row}]/td[4]/form/button")))
        generar_csv.click()
        time.sleep(3)
        descargar_csv = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[{row}]/td[5]/a/button/span")))
        descargar_csv.click()
        time.sleep(3)
    except TimeoutException as e:
        print(f"Error exporting CSV for row {row}: TimeoutException: {e}")
    except NoSuchElementException as e:
        print(f"Error exporting CSV for row {row}: NoSuchElementException: {e}")

def main():
    driver = setup_driver()
    username = "COMERCIAL@TRIFORFUN.ES"
    password = "tffpsswrd"
    login(driver, username, password)
    navigate_to_export_page(driver)
    export_csv(driver, 7)
    export_csv(driver, 9)
    driver.quit()

if __name__ == "__main__":
    main()