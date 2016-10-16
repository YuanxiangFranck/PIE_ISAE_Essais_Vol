# Dépôt de code pour le PIE

## Python

### Virtual env

Pour développer en python il est souvent conseillé de coder dans un environnement
virtuel. Un environnement virtuel c'est simplement un environnement qui utilisera
seulement quelques paquets installé a la version demandée.
L'avantage c'est que vous pouvez par exemple garder python2 avec les paquets que
vous avez et travailler dans un environnement indépendant avec python3 et
d'autres paquets.

Comment installer un environnement virtuel avec pip avec un terminal:
(je n'ai jamais fait avec anaconda, ni essayé sous windows)

Installer virtualenv: `pip install --user virtualenv`
Créer un environnement virtuel: `mkvirtualenv -p python3 pie2016`
Entrée dans un environnement virtuel `source ~/.virtualenvs/pie2016/bin/activate`

Pour changer d'environnement virtuel plus facilement vous pouvez installer [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/). Cela permet d'activer un environnement virtuel avec `workon pie2016` (avec auto complétion)

Dans l'environnement virtuel, vous pouvez facilement vérifier que l'interpréteur python est celui de l'environnement sélectionné avec:
```shell
$ which python
/home/franck/.virtualenvs/pie2016/bin/python
```

### Installer les paquets

`pip install *nom_paquet*`
Pour installer les paquets défini dans le fichier `requierement.txt`: `pip install -r requierement.txt`
Pensez à ajouter le paquet installé dans le fichier `requierement.txt`.
Pour retrouver la version du paquet (et la syntaxe du requierement.txt): `pip freeze`
