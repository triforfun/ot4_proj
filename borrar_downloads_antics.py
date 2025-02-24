import os
import shutil
from os import remove
from pathlib import Path

on_esborrar="c:/usersonlin/downloads/"

ficherolog="C:/py_rafa/descarregues.log"
destinoBLUNAE="c:/users/onlin/downloads/informe-maesarti.csv"
destinoSPIUK="c:/usersonlin/downloads/stocks-spiuk*.csv"
destinoHB1="c:/usersonlin/downloads/extract_produits.csv"
destinoHB2="c:/usersonlin/downloads/extract_produits_tailles.csv"
destinoORCA = "c:/usersonlin/downloads/list.csv"
print(destinoBLUNAE)

if Path(destinoBLUNAE).is_file():
    print("existe Fichero Blunae, HO ESBORRO")
    remove(destinoBLUNAE)
else:
    print("no existe fichero Blunae")

if Path(destinoSPIUK).is_file():
    print("existe Fichero Spiuk, HO ESBORRO")
    remove(destinoSPIUK)
else:
    print("no existe fichero Spiuk")

if Path(destinoHB1).is_file():
    print("existe produits, HO ESBORRO")
    remove(destinoHB1)
else:
    print("no existen produits")

if Path(destinoHB2).is_file():
    print("existe produits_tailles, HO ESBORRO")
    remove(destinoHB2)
else:
    print("no existen produits_tailles")

if Path(destinoORCA).is_file():
    print("existe ORCA, HO ESBORRO")
    remove(destinoHB2)
else:
    print("no existen ORCA")

