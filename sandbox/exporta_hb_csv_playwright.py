import os
import asyncio
import shutil
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

async def main():
    # Ruta de descarga y rutas de destino
    ruta_descarga = 'C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS'
    ruta_backup = 'C:/TFF/DOCS/ONLINE/STOCKS_BACKUP'
    fich1 = 'extract_produits.csv'
    fich2 = 'extract_produits_tailles.csv'

    # Asegúrate de que las rutas de destino existan
    os.makedirs(ruta_descarga, exist_ok=True)
    os.makedirs(ruta_backup, exist_ok=True)

    # Configuración de Playwright
    async with async_playwright() as p:
        # Inicia el navegador en modo no headless
        browser = await p.chromium.launch(headless=True)

        # Configura el contexto del navegador para aceptar descargas
        context = await browser.new_context(accept_downloads=True)

        page = await context.new_page()

        # Escuchar eventos de descarga
        async def on_download(download):
            # Esperar a que la descarga se complete
            path = await download.path()
            # Mover el archivo descargado a la ruta deseada
            if download.url.endswith(fich1) or download.url.endswith(fich2):
                shutil.move(path, os.path.join(ruta_descarga, download.suggested_filename))

        page.on("download", lambda download: asyncio.create_task(on_download(download)))

        print("Comença la exportació dels fitxers de productes i variants de la web de Triforfun")

        # Navegar a la URL
        await page.goto("http://triforfun.hiboutik.com/")

        # Rellenar el formulario de login
        await page.fill("input[name='login_user']", "comercial@triforfun.es")
        await page.fill("input[name='pass_user']", "tffpsswrd")

        # Hacer clic en el botón de submit
        await page.click("button[type='submit']")

        # Navegar a través de los menús
        await page.click("xpath=/html/body/div[2]/nav/div/ul/li[4]/form")
        await page.click("xpath=//li/ul/li/form/button[@type='submit'][@value='Importar-Exportar']")
        await page.click("xpath=/html/body/div[2]/nav/div/ul/li[4]/ul/li[7]/form")

        # Exportar datos
        await page.click("xpath=/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[1]/h4/a")

        # Generar y descargar CSV
        await page.click("xpath=/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[7]/td[4]/form/button/span")
        await asyncio.sleep(3)
        await page.click("xpath=/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[7]/td[5]/a/button/span")

        await asyncio.sleep(3)

        await page.click("xpath=/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[9]/td[4]/form/button")
        await asyncio.sleep(3)
        await page.click("xpath=/html/body/div[2]/div/div[3]/div/div/div/div/div/div[1]/div[2]/div/table/tbody/tr[9]/td[5]/a/button/span")

        print("Ha acabat la descàrrega dels 2 fitxers")

        await asyncio.sleep(10)

        # Cerrar el navegador
        await browser.close()

    # Mover archivos existentes a backup con timestamp
    for fich in [fich1, fich2]:
        ruta_fichero_final = os.path.join(ruta_descarga, fich)
        if os.path.exists(ruta_fichero_final):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            nuevo_nombre = f"{os.path.splitext(fich)[0]}_{timestamp}{os.path.splitext(fich)[1]}"
            shutil.move(ruta_fichero_final, os.path.join(ruta_backup, nuevo_nombre))

    # Eliminar backups con más de 15 días de antigüedad
    ahora = datetime.now()
    for fich in os.listdir(ruta_backup):
        ruta_fichero_backup = os.path.join(ruta_backup, fich)
        fecha_modificacion = datetime.fromtimestamp(os.path.getmtime(ruta_fichero_backup))
        if ahora - fecha_modificacion > timedelta(days=15):
            os.remove(ruta_fichero_backup)

# Ejecutar la función principal
asyncio.run(main())
