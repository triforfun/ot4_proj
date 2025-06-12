"""
baixa el fitxer d'stock de blunae i cdc per ftp
"""
import os
import subprocess

# Definir rutas de archivos y comandos
WINSCP_PATH = 'C:/Program Files (x86)/WinSCP/WinSCP.com'
SCRIPT_FN1 = 'C:/Program Files (x86)/WinSCP/prova1ot4.txt'
SCRIPT_FN2 = 'C:/Program Files (x86)/WinSCP/stockcdc.txt'
LOG_FN = 'log.txt'
FICH1_PATH = "c:/users/onlin/downloads/informe-maesarti.csv"

def run_winscp_script(script_fn, log_fn):
    try:
        subprocess.run([
            WINSCP_PATH,
            '/script=' + script_fn,
            '/log=' + log_fn,
            '/ini=nul'
        ], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script {script_fn}: {e}")

# Ejecutar scripts
run_winscp_script(SCRIPT_FN1, LOG_FN)
# run_winscp_script(SCRIPT_FN2, LOG_FN) aquest era per baixar el stock de cdc peroò ja no ho fem servir

# Verificar y eliminar archivo si existe
if not os.path.exists(FICH1_PATH):
    print("NO EXISTEn los ficheros", FICH1_PATH)
else:
    os.remove(FICH1_PATH)
    print("borrados los ficheros", FICH1_PATH)