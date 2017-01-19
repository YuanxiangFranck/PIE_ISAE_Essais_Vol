# Documentation

La documentation est directement généré à partir du code (docstring) et disponible à l'adresse : https://yuanxiangfranck.github.io/PIE_ISAE_Essais_Vol/

Pour plus d'infomations pour générer la documentation: [docs/README.md](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/docs/README.md)

# Python

Il existe plusieurs méthodes pour développer sous ce projet.

## Anaconda (tous OS)

Un bundle avec toute les librairies nécessaire pour faire tourner et développer le projet.
Anaconda comprend notamment :
* Python (interpréteur Python/IPython + IDA Spyder + Notebooks Jupyter)
* numpy, scipy, scikit-learn, et autres librairies scientifiques

## Virtual env + pip (OSX / Linux)

### Installer les paquets (pip)

`pip install *nom_paquet*`
Pour installer les paquets définis dans le fichier `requierement.txt`: `pip install -r requierement.txt`
Pensez à ajouter le paquet installé dans le fichier `requierement.txt`.
Pour retrouver la version du paquet (et la syntaxe du requierement.txt): `pip freeze`

### Virtual env

Installer virtualenv: `pip install --user virtualenv`
Créer un environnement virtuel: `mkvirtualenv -p python3 pie2016`
Entrée dans un environnement virtuel `source ~/.virtualenvs/pie2016/bin/activate`

Pour changer d'environnement virtuel plus facilement, vous pouvez installer [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/). Cela permet d'activer un environnement virtuel avec `workon pie2016` (avec autocomplétion)
