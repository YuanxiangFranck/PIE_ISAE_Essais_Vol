# html_pages

Fichier html, css et JavaScript pour générer la page html qui résume un vol.

# parser.py

Contient la fonction pour parser les fichiers de données

Attention le parser ne prend pas en compte les unités pour l'instant

## Cas spéciaux pour les signaux de régulation

Pour les signaux de régulation il y a des des signaux du type: 41psig
Ces colonnes ne sont pas dans les données donc elles sont ajouté manuellement par le parser


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
