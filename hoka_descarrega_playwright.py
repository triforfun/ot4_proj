import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Escribe tu contraseña aquí. ¡Y cámbiala en la web del proveedor!
# PASSWORD = "TU_CONTRASEÑA_AQUÍ"
PASSWORD = "HokaTff2022"

# Datos que me proporcionaste
LOGIN_URL = "https://comercialudrab2b.elasticsuite.com/"
USERNAME = "info@triforfun.es"
DOWNLOAD_PATH = r"C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\HOKA"
CATALOGOS_A_DESCARGAR = ["HOKA SS25 Especialista", "HOKA FW24 Especialista"]

# --- INICIO DEL SCRIPT ---
def run_automation():
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
        print(f"Directorio creado: {DOWNLOAD_PATH}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # 1. Iniciar sesión y navegar al informe
            print("Iniciando sesión y navegando...")
            page.goto(LOGIN_URL, timeout=60000)
            page.locator('input[name="username"]').wait_for(timeout=60000)
            page.locator('input[name="username"]').fill(USERNAME)
            page.locator('input[name="password"]').fill(PASSWORD)
            page.get_by_role("button", name="Iniciar sesión").click()

            gestiona_menu = page.get_by_text("Gestiona", exact=True)
            gestiona_menu.wait_for(timeout=60000)
            gestiona_menu.hover()

            page.get_by_text("Informe de inventario", exact=True).click()
            print("Página de inventario cargada.")

            # 3. Descargar los ficheros
            for catalogo in CATALOGOS_A_DESCARGAR:
                print(f"--- Procesando catálogo: {catalogo} ---")

                print("Abriendo el desplegable de 'Catálogo'...")
                page.locator("div.css-13483rh-control").nth(1).click()

                print(f"Seleccionando la opción '{catalogo}'...")
                page.get_by_text(catalogo, exact=True).click()

                # --- LÓGICA CORREGIDA PARA LA CASILLA DE VERIFICACIÓN ---
                # Usamos get_by_label para encontrar la casilla por su texto asociado
                checkbox_futura = page.get_by_label("Incluir disponibilidad futura")
                if checkbox_futura.is_checked():
                    checkbox_futura.uncheck()
                    print("Checkbox 'Disponibilidad futura' desmarcado.")

                with page.expect_download() as download_info:
                    page.get_by_role("button", name="Enviar").click()
                    print("Botón 'Enviar' pulsado. Esperando descarga...")

                download = download_info.value
                file_name = f"{catalogo.replace(' ', '_')}.xlsx"
                save_path = os.path.join(DOWNLOAD_PATH, file_name)

                download.save_as(save_path)
                print(f"ÉXITO: Fichero '{download.suggested_filename}' guardado como '{file_name}' en {DOWNLOAD_PATH}")

                time.sleep(3)

        except TimeoutError as e:
            print("\nERROR: La página tardó demasiado en responder o un elemento no se encontró a tiempo.")
            print(f"Detalle del error: {e}")
        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
        finally:
            print("Proceso finalizado. Cerrando navegador.")
            browser.close()


if __name__ == "__main__":
    if PASSWORD == "TU_CONTRASEÑA_AQUÍ" or not PASSWORD:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! POR FAVOR, ABRE EL FICHERO .py Y EDITA LA CONTRASEÑA !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        run_automation()