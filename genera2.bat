echo Empieza el proceso de generación de stocks
rem @echo off
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
echo [%TIMESTAMP%] %* >> "%LOG_FILE%"
echo %* >> "%LOG_FILE%"
goto :eof

:: Eliminar logs antiguos (más de 15 días)
forfiles /P "%LOG_DIR%" /M %SCRIPT_NAME%.log /D -15 /C "cmd /c del @path"
call :log "Eliminados logs antiguos de más de 15 días."

:: Guardar el tiempo de inicio
set START_TIME=%TIME%
call :log "Inicio del proceso: %START_TIME%"

:: Ejecutar el script de Python para descargar archivos FTP
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
    python %%S || (
        call :log "Error al ejecutar %%S"
        exit /b 1
    )
)

:: Mover archivos descargados
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
move /Y c:\users\onlin\downloads\list.csv C
