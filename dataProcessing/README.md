# html_pages

Fichier html, css et JavaScript pour générer la page html qui résume un vol.

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

# parser.py

Contient la fonction pour parser les fichiers de données

# plotter.py

Contient les fonctions pour plotter les données

# segmenter.py

Continent la fonctions pour calculer la segmentation d'un vol

# segmenter_utils.py

Contient des fonctions pour aider le calcul de la segmentation de vol

# summary.py

Contient la fonction qui permet d'exporter la page html des données
cf : html_pages

# utils.py

fonctions utilitaires
* vérifier l'existence d'un chemin + création des dossiers si besoin
