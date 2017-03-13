# README pour le dossier algorithms

Ce document a pour vocation d'expliquer de façon haut niveau tous les scripts présents dans le dossier *algorithms* et de faciliter leur utilisation. 

## Symmetry.py

Ce script regroupe toutes les fonctions utilisées pour la détection d'anomalies un vol en utilisant le modèle de symétrie latérale avion et de redondance calculateur.
Celles-ci sont potentiellement appelées par le script `asymmetry_detection`.
On y trouve notamment :
* les fonctions d'extraction de paires de signaux censées être égales
* les fonctions de test d'erreur relative entre deux signaux
* une fonction qui traite le cas de symétrie latérale 
* une fonction qui traite le cas de redondance
* les fonctions d'écriture des fichiers de résultats

## symmetry_anomaly_detection.py

Ce script comporte une unique fonction, `asymmetry_detection`, qui permet d'effectuer un test général de symétries. Il fait appel aux fonctions définies dans `Symmetry.py`.
À partir des données de vol et d'un seuil d'erreur relative, le script calcule la durée de vol anormal pour chaque couple de signaux censés être égaux ainsi que leurs coefficients de regression linéaire. Enfin, le script peut génèrer des documents de sortie regroupant les résultats obtenus (par appel aux fonctions d'écriture de `Symmetry.py`).


Exemple d'utilisation

```python
from iliad import Iliad

path = "./data/data.txt" # Chemin vers les données de vol
config_path="./dataProcessing/config.json" # Chemin vers un fichier de configuration

anomaly_detector = Iliad(path, verbose=True) # ou verbose=False

error = 0.01 # Pour un seuil d'erreur relative de 1%
save_csv = True # Pour sauver les résultats en un fichier de sortie csv
save_txt = True # Pour sauver les résultats en un fichier de sortie txt
out_filename = "auto"  # Génaration automatique du nom de sauvegarde
out_dir = "./resultats/" # Chemin relatif vers le dossier où sauvegarder les résultats

anomaly_detector.export_asymmetry_detection(error = error, save_csv = save_csv, save_txt = save_txt,  out_filename = out_filename, out_dir = out_dir)

# En effet, la fonction export_asymmetry_detection appelle directement asymmetry_detection.
```
