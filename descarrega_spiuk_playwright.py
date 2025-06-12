from playwright.sync_api import sync_playwright

def download_spiuk_stock():
    url = "https://www.spiuk.pro/es/"

    with sync_playwright() as p:
        # Configurar el navegador (Chromium en este caso)
        browser = p.chromium.launch(headless=False)  # Cambia a True para modo headless
        page = browser.new_page()

        print("Comienza la descarga de SPIUK")

        # Navegar a la URL
        page.goto(url)

        # Rellenar el campo "Delegacion"
        page.fill('input[name="Delegacion"]', "5962")

        # Rellenar el campo "Clave"
        page.fill('input[name="Clave"]', "03130524")

        # Hacer clic en el botón "Acceder"
        page.click('xpath=/html/body/main/div/div/form/div[3]/button')

        # Esperar a que se complete la acción
        page.wait_for_timeout(10000)  # Espera 10 segundos

        # Hacer clic en "Descargas"
        page.click('xpath=/html/body/header/div[1]/nav/div/ul/li[3]/a')

        # Esperar a que se complete la acción
        page.wait_for_timeout(3000)  # Espera 3 segundos

        # Hacer clic en "Stock CSV"
        page.click('xpath=/html/body/header/div[1]/nav/div/ul/li[3]/ul/li[1]/a')

        # Esperar a que se complete la acción
        page.wait_for_timeout(1000)  # Espera 1 segundo

        print("Acabó descarga de SPIUK")

        # Cerrar el navegador
        browser.close()

download_spiuk_stock()
