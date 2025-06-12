@echo off
setlocal enabledelayedexpansion

:: Configuración de rutas y nombres de archivos
set LOG_DIR=C:\TFF\DOCS\ONLINE\STOCKS_BACKUP
set LOG_FILE=%LOG_DIR%\%~n0.log
set SCRIPT_NAME=%~n0

:: Crear el directorio de logs si no existe
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Función para añadir una entrada al log con timestamp
:log
set TIMESTAMP=%DATE% %TIME%
echo [%TIMESTAMP%] %*
echo [%TIMESTAMP%] %* >> "%LOG_FILE%"
goto :eof

:: Eliminar logs antiguos (más de 15 días)
call :log "Eliminando logs antiguos de más de 15 días..."
forfiles /P "%LOG_DIR%" /M %SCRIPT_NAME%.log /D -15 /C "cmd /c del @path"

:: Mensaje de inicio en consola y log
call :log "Inicio del proceso: %TIME%"

:: Guardar el tiempo de inicio
set START_TIME=%TIME%

:: Ejecutar el script de Python para descargar archivos FTP
call :log "Ejecutando descarrega_ftp.py..."
python c:\soft_proj\ot4_proj\descarrega_ftp.py || (
    call :log "Error al ejecutar descarrega_ftp.py"
    exit /b 1
)

:: Eliminar archivos existentes
set FILES_TO_DELETE="c:\users\onlin\downloads\informe-maes*.csv" "c:\users\onlin\downloads\custom.csv" "c:\users\onlin\downloads\arena*.xlsx" "c:\users\onlin\downloads\stocks-spiuk*.csv" "c:\users\onlin\downloads\extract_produits*.csv" "c:\users\onlin\downloads\extract_produits_tailles*.csv" "c:\users\onlin\downloads\list*.csv" "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA FW24.XLSX" "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA ss25.XLSX"

for %%F in (%FILES_TO_DELETE%) do (
    if exist %%F (
        del /f %%F
        call :log "Archivo eliminado: %%F"
    )
)

:: Ejecutar scripts de Python para descargar y procesar datos
set PYTHON_SCRIPTS="c:\soft_proj\ot4_proj\hoka_descarrega_playwright.py" "c:\soft_proj\ot4_proj\descarrega_spiuk_playwright.py" "C:\soft_proj\ot4_proj\exporta_fitxers_diaris_hb_playwright.py" "c:\soft_proj\ot4_proj\descarrega_orca_playwright.py" "c:\soft_proj\ot4_proj\descarregaSF_BL.py"

for %%S in (%PYTHON_SCRIPTS%) do (
    call :log "Ejecutando %%S..."
    python %%S || (
        call :log "Error al ejecutar %%S"
        exit /b 1
    )
)

:: Mover archivos descargados
call :log "Moviendo archivos descargados..."
move /Y c:\users\onlin\downloads\informe-maesarti.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS || (
    call :log "Error al mover informe-maesarti.csv"
    exit /b 1
)
move /Y c:\users\onlin\downloads\stocks-spiuk.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS || (
    call :log "Error al mover stocks-spiuk.csv"
    exit /b 1
)
move /Y c:\users\onlin\downloads\custom.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS || (
    call :log "Error al mover custom.csv"
    exit /b 1
)
move /Y c:\users\onlin\downloads\list.csv C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ORCA\STOCK_ORCA.CSV || (
    call :log "Error al mover list.csv"
    exit /b 1
)

:: Ejecutar script de Python para mover ficheros
call :log "Ejecutando mover_ficheros.py..."
python c:\soft_proj\ot4_proj\mover_ficheros.py || (
    call :log "Error al ejecutar mover_ficheros.py"
    exit /b 1
)

:: Calcular el tiempo transcurrido
set END_TIME=%TIME%
call :log "Fin del proceso: %END_TIME%"

:: Convertir el tiempo a segundos para calcular la diferencia
set /a START_HOURS=1%START_TIME:~0,2%-100
set /a START_MINUTES=1%START_TIME:~3,2%-100
set /a START_SECONDS=1%START_TIME:~6,2%-100
set /a END_HOURS=1%END_TIME:~0,2%-100
set /a END_MINUTES=1%END_TIME:~3,2%-100
set /a END_SECONDS=1%END_TIME:~6,2%-100

set /a TOTAL_SECONDS=(%END_HOURS%*3600+%END_MINUTES%*60+%END_SECONDS%)-(%START_HOURS%*3600+%START_MINUTES%*60+%START_SECONDS%)

:: Mostrar el tiempo transcurrido
call :log "Tiempo total de ejecución: %TOTAL_SECONDS% segundos"

endlocal
