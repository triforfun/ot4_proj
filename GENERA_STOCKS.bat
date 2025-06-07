@echo off
setlocal

:: Guardar el tiempo de inicio
set START_TIME=%TIME%

python c:\soft_proj\ot4_proj\descarrega_ftp.py

if exist c:\users\onlin\downloads\informe-maes*.csv (
	del /f c:\users\onlin\downloads\informe-maes*.csv
)

if exist c:\users\onlin\downloads\custom.csv (
	del /f c:\users\onlin\downloads\custom.csv
)

if exist c:\users\onlin\downloads\arena*.xlsx (
	del /f c:\users\onlin\downloads\arena*.xlsx
)

if exist c:\users\onlin\downloads\stocks-spiuk*.csv (
	del /f c:\users\onlin\downloads\stocks-spiuk*.csv
)

if exist c:\users\onlin\downloads\extract_produits*.csv (
	del /f c:\users\onlin\downloads\extract_produits*.csv
)

if exist c:\users\onlin\downloads\extract_produits_tailles*.csv (
	del /f c:\users\onlin\downloads\extract_produits_tailles*.csv
)

if exist c:\users\onlin\downloads\list*.csv (
	del /F c:\users\onlin\downloads\list*.csv
)

if exist "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA FW24.XLSX" (
	del /F "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA FW24.XLSX"
)

if exist "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA ss25.XLSX" (
	del /F "C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ARENA\ARENA ss25.XLSX"
)

python c:\soft_proj\ot4_proj\hoka_descarrega_playwright.py
python c:\soft_proj\ot4_proj\descarregaSPIUK.py
python c:\soft_proj\ot4_proj\exportaHBcsv.py
python c:\soft_proj\ot4_proj\descarrega_orca.py
python c:\soft_proj\ot4_proj\descarregaSF_BL.py

move /Y c:\users\onlin\downloads\informe-maesarti.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
move /Y c:\users\onlin\downloads\stocks-spiuk.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
move /Y c:\users\onlin\downloads\extract_produits.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
move /Y c:\users\onlin\downloads\extract_produits_tailles.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
move /Y c:\users\onlin\downloads\custom.csv c:\TFF\DOCS\ONLINE\STOCKS_EXTERNS
move /Y c:\users\onlin\downloads\list.csv C:\TFF\DOCS\ONLINE\STOCKS_EXTERNS\ORCA\STOCK_ORCA.CSV

python c:\soft_proj\ot4_proj\mover_ficheros.py
rem python c:\soft_proj\ot4_proj\actua_stock_hoka_2_seasons_con_fechas.py

:: Calcular el tiempo transcurrido
set END_TIME=%TIME%

:: Convertir el tiempo a segundos para calcular la diferencia
set /a START_HOURS=%START_TIME:~0,2%
set /a START_MINUTES=%START_TIME:~3,2%
set /a START_SECONDS=%START_TIME:~6,2%
set /a END_HOURS=%END_TIME:~0,2%
set /a END_MINUTES=%END_TIME:~3,2%
set /a END_SECONDS=%END_TIME:~6,2%

set /a TOTAL_SECONDS=(%END_HOURS%*3600+%END_MINUTES%*60+%END_SECONDS%)-(%START_HOURS%*3600+%START_MINUTES%*60+%START_SECONDS%)

:: Mostrar el tiempo transcurrido
echo Tiempo total de ejecución: %TOTAL_SECONDS% segundos

REM PAUSE
