@echo off
setlocal enabledelayedexpansion

:: Configuración de logging
set LOG_DIR=C:\TFF\DOCS\ONLINE\STOCKS_BACKUP
set TIMESTAMP=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\stocks_process_%TIMESTAMP%.log

:: Crear directorio de logs si no existe
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    call :log "Directorio de logs creado: %LOG_DIR%"
)

:: Limpiar logs antiguos (más de 14 días)
call :cleanup_old_logs

:: Guardar el tiempo de inicio
set START_TIME=%TIME%
call :log "============================================"
call :log "INICIO DEL PROCESO DE DESCARGA DE STOCKS"
call :log "Fecha y hora: %DATE% %START_TIME%"
call :log "============================================"

:: Ejecutar el script de Python para descargar archivos FTP
call :log "Ejecutando descarrega_ftp.py..."
python c:\soft_proj\ot4_proj\descarrega_ftp.py
if errorlevel 1 (
    call :log "ERROR: Fallo al ejecutar descarrega_ftp.py"
    goto :calculate_time
) else (
    call :log "OK: descarrega_ftp.py ejecutado correctamente"
)

:: Eliminar archivos existentes
call :log "Eliminando archivos existentes..."
set FILES_TO_DELETE="c:\users\onlin\downloads\informe-maes*.csv" "c:\users\onlin\downloads\custom.csv" "c:\users\onlin\downloads\arena*.xlsx" "c:\users\onlin\downloads\stocks-spiuk*.csv" "c:\users\onlin\downloads\extract_produits*.csv" "c:\users\onlin\downloads\extract_produits_tailles*.csv" "c:\users\onlin\downloads\list*.csv" "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA FW24.XLSX" "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA ss25.XLSX"

for %%F in (%FILES_TO_DELETE%) do (
    if exist %%F (
        del /f %%F
        call :log "Archivo eliminado: %%F"
    )
)

:: Ejecutar scripts de Python para descargar y procesar datos
call :log "Ejecutando scripts de descarga y procesamiento..."
set PYTHON_SCRIPTS="c:\soft_proj\ot4_proj\hoka_descarrega_playwright.py" "c:\soft_proj\ot4_proj\descarrega_spiuk_playwright.py" "C:\soft_proj\ot4_proj\exporta_fitxers_diaris_hb_playwright.py" "c:\soft_proj\ot4_proj\descarrega_orca_playwright.py" "c:\soft_proj\ot4_proj\descarregaSF_BL.py"

for %%S in (%PYTHON_SCRIPTS%) do (
    call :log "Ejecutando: %%S"
    python %%S
    if errorlevel 1 (
        call :log "ERROR: Fallo al ejecutar %%S"
        goto :calculate_time
    ) else (
        call :log "OK: %%S ejecutado correctamente"
    )
)

:: Mover archivos descargados
call :log "Moviendo archivos descargados..."

call :log "Moviendo informe-maesarti.csv..."
move /Y c:\users\onlin\downloads\informe-maesarti.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
if errorlevel 1 (
    call :log "ERROR: Fallo al mover informe-maesarti.csv"
    goto :calculate_time
) else (
    call :log "OK: informe-maesarti.csv movido correctamente"
)

call :log "Moviendo stocks-spiuk.csv..."
move /Y c:\users\onlin\downloads\stocks-spiuk.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
if errorlevel 1 (
    call :log "ERROR: Fallo al mover stocks-spiuk.csv"
    goto :calculate_time
) else (
    call :log "OK: stocks-spiuk.csv movido correctamente"
)

call :log "Moviendo custom.csv..."
move /Y c:\users\onlin\downloads\custom.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
if errorlevel 1 (
    call :log "ERROR: Fallo al mover custom.csv"
    goto :calculate_time
) else (
    call :log "OK: custom.csv movido correctamente"
)

call :log "Moviendo list.csv..."
move /Y c:\users\onlin\downloads\list.csv C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ORCA\STOCK_ORCA.CSV
if errorlevel 1 (
    call :log "ERROR: Fallo al mover list.csv"
    goto :calculate_time
) else (
    call :log "OK: list.csv movido correctamente"
)

:: Ejecutar script de Python para mover ficheros
call :log "Ejecutando mover_ficheros.py..."
python c:\soft_proj\ot4_proj\mover_ficheros.py
if errorlevel 1 (
    call :log "ERROR: Fallo al ejecutar mover_ficheros.py"
    goto :calculate_time
) else (
    call :log "OK: mover_ficheros.py ejecutado correctamente"
)

:calculate_time
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
call :log "============================================"
call :log "Tiempo total de ejecución: %TOTAL_SECONDS% segundos"
call :log "Log guardado en: %LOG_FILE%"
call :log "============================================"

endlocal
exit /b

:: Función para escribir al log y mostrar en pantalla
:log
echo %~1
echo [%DATE% %TIME%] %~1 >> "%LOG_FILE%"
goto :eof

:: Función para limpiar logs antiguos (más de 14 días)
:cleanup_old_logs
call :log "Limpiando logs antiguos (más de 14 días)..."

:: Usar forfiles para eliminar archivos más antiguos de 14 días
forfiles /p "%LOG_DIR%" /m "stocks_process_*.log" /d -14 /c "cmd /c del @path && echo Eliminado log antiguo: @file" 2>nul

if errorlevel 1 (
    call :log "No se encontraron logs antiguos para eliminar"
) else (
    call :log "Logs antiguos eliminados correctamente"
)
goto :eof