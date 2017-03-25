
# config.json

Fichier de configuration par défaut de la classe Iliad



name  | Description | valeur
------|-------------|--------
sep | séparateur entre chaque colonne dans le fichier de texte | \t (tab)
skiprows | nombre de lignes dans le header à ignorer | 11
time\_step | le temps entre deux échantillons de temps (s) | 1
target\_precisions\_path | chemin vers le csv contenant les target | algorithms/target_precisions.csv
regulation | liste noms des signaux de régulation | ...
target | lite des noms des targets | ...
binary | liste des noms des signaux binaire | ...
endogene | liste des noms des signaux endogene | ...
phases\_colors | choix de color map pour les phases | ...
ports\_colors | choix de color map pour les ports | ...
signal\_names | noms de signaux important

# signal_names

Noms des signaux
* signal_names_bin
* signal_names_endogene
* signal_names_for_segmentation
* signal_names_regul
* target_names_regul

# units

dictionnaire avec les unitées

# target_precisions.csv

csv avec la precision pour chaque target
