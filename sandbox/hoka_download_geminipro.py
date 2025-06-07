import os
import time
from playwright.sync_api import sync_playwright, TimeoutError

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Escribe tu contraseña aquí dentro de las comillas
PASSWORD = "HokaTff2022"

# Datos que me proporcionaste
LOGIN_URL = "https://comercialudrab2b.elasticsuite.com/"
USERNAME = "info@triforfun.es"
DOWNLOAD_PATH = r"C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\HOKA"
CATALOGOS_A_DESCARGAR = ["Hoka SS25 Especialista", "Hoka FW24 Especialista"]

# --- INICIO DEL SCRIPT ---
def run_automation():
    # Asegurarse de que el directorio de descarga existe
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
        print(f"Directorio creado: {DOWNLOAD_PATH}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # headless=False para ver lo que hace
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            # 1. Iniciar sesión
            print(f"Accediendo a {LOGIN_URL}...")
            page.goto(LOGIN_URL, timeout=60000)

            print("Introduciendo credenciales...")
            page.locator('input[name="login[username]"]').fill(USERNAME)
            page.locator('input[name="login[password]"]').fill(PASSWORD)
            page.get_by_role("button", name="Iniciar sesión").click()
            print("Inicio de sesión completado.")

            # Esperar a que la página de gestión esté disponible
            page.wait_for_selector('//a[contains(text(), "Gestiona")]', timeout=60000)

            # 2. Navegar al informe de inventario
            print("Navegando al informe de inventario...")
            page.hover('//a[contains(text(), "Gestiona")]')
            page.get_by_role("menuitem", name="Informe - Inventario").click()
            print("Página de inventario cargada.")

            # 3. Descargar los ficheros
            for catalogo in CATALOGOS_A_DESCARGAR:
                print(f"Procesando catálogo: {catalogo}...")

                # Seleccionar el catálogo en el desplegable
                page.locator('select[name="catalog_id"]').select_option(label=catalogo)

                # Desmarcar la casilla "Incluir disponibilidad futura"
                if page.locator('input[name="include_future_stock"]').is_checked():
                    page.locator('input[name="include_future_stock"]').uncheck()
                    print("Checkbox 'Disponibilidad futura' desmarcado.")

                # Iniciar la descarga y esperar a que comience
                with page.expect_download() as download_info:
                    page.get_by_role("button", name="Enviar").click()
                    print("Botón 'Enviar' pulsado. Esperando descarga...")

                download = download_info.value

                # Construir la ruta de guardado y guardar el fichero
                # El nombre del fichero se coge del propio desplegable para que sea descriptivo
                file_name = f"{catalogo.replace(' ', '_')}.xlsx"
                save_path = os.path.join(DOWNLOAD_PATH, file_name)

                # Guardar y sobrescribir si ya existe
                download.save_as(save_path)
                print(f"ÉXITO: Fichero '{download.suggested_filename}' guardado como '{file_name}' en {DOWNLOAD_PATH}")

                # Pequeña pausa para asegurar que la página se resetea
                time.sleep(3)

        except TimeoutError:
            print("ERROR: La página tardó demasiado en cargar. Revisa tu conexión o la URL.")
        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
        finally:
            # 4. Cerrar el navegador
            print("Proceso finalizado. Cerrando navegador.")
            browser.close()

if __name__ == "__main__":
    if PASSWORD == "TU_CONTRASEÑA_AQUÍ":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! POR FAVOR, ABRE EL FICHERO .py Y EDITA LA CONTRASEÑA !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        run_automation()