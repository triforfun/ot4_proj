from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def download_orca_stock():
    url = "https://www.orbea.com/es-es/kide/acceso/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Cambia a True si deseas modo headless
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            print("Navegando a la página de login:", url)
            page.goto(url)

            # Esperar y llenar el campo de usuario
            user_field = page.wait_for_selector('#login_email', state="visible", timeout=60000)
            user_field.fill("TRIFORFUN")
            print("Usuario ingresado")

            # Esperar y llenar el campo de contraseña
            password_field = page.wait_for_selector('input[name="login_password"]', state="visible", timeout=60000)
            password_field.fill("kide183@")
            print("Contraseña ingresada")

            # Hacer clic en el botón "Acceder"
            page.click('button:text("Acceder")')
            print("Sesión iniciada")

            # Esperar a que la página cargue completamente después del inicio de sesión
            page.wait_for_timeout(3000)

            # Manejar el banner de cookies
            try:
                cookie_button = page.wait_for_selector('#onetrust-accept-btn-handler', timeout=10000)
                page.evaluate('''selector => {
                    document.querySelector(selector).scrollIntoView();
                }''', '#onetrust-accept-btn-handler')
                page.wait_for_timeout(1000)
                cookie_button.click()
                print("Cookies aceptadas")
            except PlaywrightTimeoutError:
                print("No se encontró el botón de cookies o ya no es necesario")

            # Navegar a la sección de disponibilidad
            disponibilidad = page.wait_for_selector('#heading > div.b2b-menu.visible > div.b2b-menu-options > div:nth-child(3) > ul > li:nth-child(3) > a', timeout=60000)
            disponibilidad.click()
            print("Navegado a la sección de disponibilidad")

            # Esperar a que la página de disponibilidad cargue completamente
            page.wait_for_timeout(3000)

            # Localizar y hacer clic en el enlace "Exportar a CSV"
            exportar_csv = page.wait_for_selector('#top > div > a:nth-child(2)', timeout=60000)
            exportar_csv.click()
            print("Exportación a CSV iniciada")

            # Esperar a que la descarga se complete
            page.wait_for_timeout(5000)

        except Exception as e:
            print(f"❌ Ocurrió un error: {e}")
            page.screenshot(path="error_screenshot.png")
            print("Se ha guardado una captura de pantalla: error_screenshot.png")

        finally:
            print("El proceso ha terminado. El navegador se cerrará en 5 segundos...")
            page.wait_for_timeout(5000)
            browser.close()
            print("Navegador cerrado.")

download_orca_stock()
