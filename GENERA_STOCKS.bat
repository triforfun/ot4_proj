@echo off
setlocal enabledelayedexpansion

:: Configuración de logging
set LOG_DIR=C:\TFF\DOCS\ONLINE\STOCKS_BACKUP\LOGSBAT
set TIMESTAMP=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set LOG_FILE=%LOG_DIR%\stocks_process_%TIMESTAMP%.log
set SCRIPT_ERRORS=0

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
call :execute_python "c:\soft_proj\ot4_proj\descarrega_ftp.py"

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
call :execute_python "c:\soft_proj\ot4_proj\hoka_descarrega_playwright.py"
call :execute_python "c:\soft_proj\ot4_proj\descarrega_spiuk_playwright.py"
call :execute_python "C:\soft_proj\ot4_proj\exporta_fitxers_diaris_hb_playwright.py"
call :execute_python "c:\soft_proj\ot4_proj\descarrega_orca_playwright.py"
call :execute_python "c:\soft_proj\ot4_proj\descarregaSF_BL.py"

:: Mostrar resumen de errores
if %SCRIPT_ERRORS% gtr 0 (
    call :log "ADVERTENCIA: Se produjeron %SCRIPT_ERRORS% errores durante la ejecución de scripts Python"
) else (
    call :log "Todos los scripts Python se ejecutaron correctamente"
)

:: Mover archivos descargados
call :log "Moviendo archivos descargados..."

call :move_file "c:\users\onlin\downloads\informe-maesarti.csv" "c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS"
call :move_file "c:\users\onlin\downloads\stocks-spiuk.csv" "c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS"
call :move_file "c:\users\onlin\downloads\custom.csv" "c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS"
call :move_file "c:\users\onlin\downloads\list.csv" "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ORCA\STOCK_ORCA.CSV"

:: Ejecutar script final de Python para mover ficheros
call :execute_python "c:\soft_proj\ot4_proj\mover_ficheros.py"

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
if %SCRIPT_ERRORS% gtr 0 (
    call :log "RESUMEN: Proceso completado con %SCRIPT_ERRORS% errores"
) else (
    call :log "RESUMEN: Proceso completado exitosamente"
)
call :log "Log guardado en: %LOG_FILE%"
call :log "============================================"

endlocal
exit /b 0

:: Función para escribir al log y mostrar en pantalla
:log
echo %~1
echo [%DATE% %TIME%] %~1 >> "%LOG_FILE%"
goto :eof

:: Función para ejecutar scripts Python con manejo de errores robusto
:execute_python
set SCRIPT_PATH=%~1
call :log "Ejecutando: %SCRIPT_PATH%"

:: Verificar que el archivo existe
if not exist "%SCRIPT_PATH%" (
    call :log "ERROR: El archivo %SCRIPT_PATH% no existe"
    set /a SCRIPT_ERRORS+=1
    goto :eof
)

:: Ejecutar el script Python y capturar el código de salida
python "%SCRIPT_PATH%"
set PYTHON_EXIT_CODE=%ERRORLEVEL%

:: Evaluar el resultado
if %PYTHON_EXIT_CODE% neq 0 (
    call :log "ERROR: El script %SCRIPT_PATH% falló con código de salida %PYTHON_EXIT_CODE%"
    set /a SCRIPT_ERRORS+=1

    :: Verificar si hay procesos Python colgados y limpiarlos
    tasklist /FI "IMAGENAME eq python.exe" /FO CSV 2>nul | find /I "python.exe" >nul
    if not errorlevel 1 (
        call :log "  Terminando procesos Python colgados..."
        taskkill /F /IM python.exe /T >nul 2>&1
    )
) else (
    call :log "OK: %SCRIPT_PATH% ejecutado correctamente"
)

goto :eof

:: Función para mover archivos con manejo de errores
:move_file
set SOURCE_FILE=%~1
set DEST_PATH=%~2
set FILE_NAME=%~nx1

call :log "Moviendo %FILE_NAME%..."

if not exist "%SOURCE_FILE%" (
    call :log "ADVERTENCIA: El archivo %SOURCE_FILE% no existe, omitiendo..."
    goto :eof
)

move /Y "%SOURCE_FILE%" "%DEST_PATH%" >nul 2>&1
if errorlevel 1 (
    call :log "ERROR: Fallo al mover %FILE_NAME%"
    set /a SCRIPT_ERRORS+=1
) else (
    call :log "OK: %FILE_NAME% movido correctamente"
)

goto :eof

:: Función para limpiar logs antiguos (más de 14 días)
:cleanup_old_logs
call :log "Limpiando logs antiguos (más de 14 días)..."

:: Usar forfiles para eliminar archivos más antiguos de 14 días
forfiles /p "%LOG_DIR%" /m "stocks_process_*.log" /d -14 /c "cmd /c del @path" 2>nul
if errorlevel 1 (
    call :log "No se encontraron logs antiguos para eliminar"
) else (
    call :log "Logs antiguos eliminados correctamente"
)
goto :eof