"""
Descarga el archivo de stock de Blunae por FTP.
"""
import os
import subprocess
from pathlib import Path

# Definir rutas de archivos y comandos
WINSCP_PATH = Path('C:/Program Files (x86)/WinSCP/WinSCP.com')
SCRIPT_FN1 = Path('C:/Program Files (x86)/WinSCP/prova1ot4.txt')
LOG_FN = Path('log.txt')
FICH1_PATH = Path("c:/users/onlin/downloads/informe-maesarti.csv")

def run_winscp_script(script_fn, log_fn):
    try:
        subprocess.run(
            [
                str(WINSCP_PATH),
                f'/script={script_fn}',
                f'/log={log_fn}',
                '/ini=nul'
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Script {script_fn} ejecutado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script {script_fn}: {e.stderr}")

def main():
    # Ejecutar script
    run_winscp_script(SCRIPT_FN1, LOG_FN)

    # Verificar y eliminar archivo si existe
    if FICH1_PATH.exists():
        try:
            FICH1_PATH.unlink()
            print(f"Archivo {FICH1_PATH} ha sido eliminado.")
        except Exception as e:
            print(f"Error al eliminar el archivo {FICH1_PATH}: {e}")
    else:
        print(f"El archivo {FICH1_PATH} no existe.")

    # Mensaje de finalización
    print("Todas las operaciones se han completado con éxito.")

if __name__ == "__main__":
    main()
