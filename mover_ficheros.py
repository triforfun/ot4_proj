import os
import shutil
from os import remove
from pathlib import Path

ficherolog="C:/py_rafa/fitxers_py/descarregues.log"
destino1="C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS"
destinohoka="C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/HOKA"
destinoArena="C:/TFF/DOCS/ONLINE/STOCKS_EXTERNS/ARENA"

fichdestino1Hoka = destinohoka+"/HOKA FW23 Especialista.xlsx"
fichdestino2Hoka = destinohoka+"/HOKA SS24 Especialista.xlsx"
fichdestinoArena = destinoArena+"/ARENA SS24.xlsx"
fichdestino_0_Arena = destinoArena+"/ARENA FW23.xlsx"

fich1Hoka = "c:/Users/onlin/Downloads/HOKA FW23 Especialista.xlsx"
fich2Hoka = "c:/users/onlin/Downloads/HOKA SS24 Especialista.xlsx"
fich1Arena = "c:/users/onlin/Downloads/ARENA SS24.xlsx"
fich0Arena = "c:/users/onlin/Downloads/ARENA FW23.xlsx"

if not os.path.exists(fich1Hoka):
    print("NO HA ENCONTRADO EL FICHERO ", fich1Hoka, "en Descargas")
else:
    print("ha encontrado el fichero de origen en Descargas ", fich1Hoka)
    if not os.path.exists(fichdestino1Hoka):
        print("no existe el fichero destino", fichdestino1Hoka)
    else:
        remove(fichdestino1Hoka)

    shutil.move(fich1Hoka, destinohoka)
    print(fich1Hoka, " movido a ", destinohoka)
        
        
if not os.path.exists(fich2Hoka):
    print("NO HA ENCONTRADO EL FICHERO ", fich2Hoka, "en Descargas")
else:
    print("ha encontrado el fichero de origen en Descargas ", fich2Hoka)
    if not os.path.exists(fichdestino2Hoka):
        print("no existe el fichero destino", fichdestino1Hoka)
    else:
        remove(fichdestino2Hoka)

    shutil.move(fich2Hoka, destinohoka)
    print(fich2Hoka, " movido a ", destinohoka)


if not os.path.exists(fich1Arena):
    print("NO HA ENCONTRADO EL FICHERO ", fich1Arena, "en Descargas")
else:
    print("ha encontrado el fichero de origen en Descargas ", fich1Arena)
    if not os.path.exists(fichdestinoArena):
        print("no existe el fichero destino", fichdestinoArena)
    else:
        remove(fichdestinoArena)
        
    shutil.move(fich1Arena, destinoArena)
    print(fich1Arena, " movido a ", destinoArena)


if not os.path.exists(fich0Arena):
    print("NO HA ENCONTRADO EL FICHERO ", fich0Arena, "en Descargas")
else:
    print("ha encontrado el fichero de origen en Descargas ", fich0Arena)
    if not os.path.exists(fichdestino_0_Arena):
        print("no existe el fichero destino", fichdestino_0_Arena)
    else:
        remove(fichdestino_0_Arena)
        
    shutil.move(fich0Arena, destinoArena)
    print(fich0Arena, " movido a ", destinoArena)
