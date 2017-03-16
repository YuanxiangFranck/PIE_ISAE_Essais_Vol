# README pour le dossier algorithms

Ce document a pour vocation d'expliquer de façon haut niveau tous les scripts présents dans le dossier *algorithms* et de faciliter leur utilisation. 

## heatmap_visualization.py

Ce fichier contient la fonction de visualisation d'une feature sur un vol sur une heatmap. Cette visualisation permet de mettre en évidence des instants particuliers du vol et possiblement des anomalies. Cette fonction :

* découpe le vol en segments temporels
* extrait une feature sur chacun de ces segments temporels et sur chaque signal (ou paire de signaux dans le cas des signaux régulation/targets)
* représente le tout sur une ou plusieurs heatmap, sur laquelle figurent également les phases du vol et les ports débitants
* enregistre le résultat en un fichier pdf ou une image si on le souhaite

Prototype de la fonction :

```python
def heatmap(flight_data=None, feature=None, signal_category=None, signal_list=None,
            time_window='auto', n_segments='auto', hclust=False, save=True,
            flight_name='undefined', out_dir='.', out_filename='auto',
            show_plot=True, out_format='pdf', annot=False, robust=True, conf=None):
```

### Découpage en segments temporels

Il faut fournir à la fonction l'un des deux arguments suivants (l'autre devant rester à sa valeur par défaut, `'auto'`) :

* `n_segments` : nombre de segments
* `time_window` : durée d'un segment

**Attention** : selon la durée du vol et le nombre/la durée des segments choisis, en raison des divisions entières effectuées, un certain nombre de pas de temps en fin de vol sont ignorés.

### Choix de la feature

La feature est sélectionnée grâce à l'argument `feature` qui doit être un nom de feature valide.

_Features portant sur les paires signaux de régulation/targets_

* `time_off_regulation` : nombre de pas de temps passés hors-régulation, selon le critère où un signal est hors-régulation à un pas de temps donné si la valeur absolue de son écart avec la target est supérieur à un certain seuil, spécifique à chaque signal. Le types d'écart (absolu ou relatif) et leur valeurs sont spécifiés dans le fichier `target_precisions.csv`, dont le chemin est fixé dans le fichier de configuration
* `percent_time_off_regulation` : pourcentage de temps passé hors-régulation (nombre de pas de temps divisé par la durée du segment temporel)
* `off_regulation_crossings` : nombre de passages du seuil de régulation, i.e. le nombre de fois où la valeur absolue de l'écart entre un signal et sa target devient supérieure ou devient inférieure au seuil spécifié dans `target_precisions.csv`

_Features portant sur les signaux binaires_

* `nb_transitions` : nombre de changements d'état du signal sur le segment temporel considéré (**Note** : peut aussi être utilisé sur tout type de signal pour compter le nombre de pas de temps où celui-ci change de valeur)

_Features utilisables sur tous types de signaux_
* `mean` : moyenne du signal sur le segment temporel considéré
* `var` : variance du signal sur le segment temporel considéré
* `std` : écart-type du signal sur le segment temporel considéré
* `min` : maximum du signal sur le segment temporel considéré
* `max` : minimum du signal sur le segment temporel considéré
* `amplitude` : amplitude signée du signal sur le segment temporel considéré

### Choix des signaux

**Note** : pour les heatmaps spécifiques `time_off_regulation`, `percent_time_off_regulation`, `off_regulation_crossings` et `nb_transitions`, il n'y a pas de choix sur les signaux. Les catégories `'regulation'` ou `'binary'` sont automatiquement sélectionnées.

Le choix des signaux se fait à l'aide des argument `signal_category` et `signal_list`. Deux possibilités sont offertes :

1. Sélectionner tous les signaux d'une catégorie de signaux avec `signal_category` (par exemple `'binary'` ou `'regulation'`) : la fonction chargera les signaux de cette catégorie à partir du fichier de configuration. Dans ce cas, l'argument `signal_list` est ignoré.
2. Sélectionner manuellement des signaux à l'aide de leur nom, dans le cas où `signal_category` est égal à `'custom'`. L'argument `signal_list` doit alors être une liste de noms de signaux.

### Mise en forme et exportation de la heatmap

L'apparence de la heatmap peut être modifiée par 3 arguments :

* `hclust` : effectuer ou non un clustering hiérarchique sur les lignes pour que les signaux similaires soient regroupés
* `annot` : afficher ou non la valeur de la feature dans chaque case de la heatmap
* `robust` : utiliser ou non une échelle de couleurs robuste (activé par défaut). Une échelle de couleurs robuste permet d'ignorer les valeurs extrêmes dans l'échelle de couleurs, afin que les variations de couleurs plus faibles restent visibles. Il faut donc faire attention au fait que les valeurs extrêmes se trouvent en-dehors des limites de l'axe des couleur sur la droite de la heatmap. Pour afficher les valeurs réelles, utiliser l'argument `annot`.

## ocsvm_anomaly_detection.py



## pca_visualization.py



## heatmap_symmetry.py

Ce script est très proche de celui 'heatmap_visualization.py', la seule différence provient du fait qu'on n'affiche non pas une matrice de features, mais une matrice qui indique pour chaque paire de sigaux et pour chaque segment temporel, la durée d'anomalie de la paire, soit le temps passé avec une erreur relative supérieure au seuil, rapporté à la durée du segment temporel. 
Par exemple, la valeur 0.8 sur une case (i,j) indique donc que sur 80% du segment temporel j, l'erreur relative des signaux composants la paire i est supérieure au seuil donné par l'utilisateur.


## Symmetry.py

Ce script regroupe toutes les fonctions utilisées pour la détection d'anomalies un vol en utilisant le modèle de symétrie latérale avion et de redondance calculateur.
Celles-ci sont potentiellement appelées par le script `asymmetry_detection`.
On y trouve notamment :
* les fonctions d'extraction de paires de signaux censées être égales
* les fonctions de test d'erreur relative entre deux signaux
* une fonction qui traite le cas de symétrie latérale 
* une fonction qui traite le cas de redondance
* les fonctions d'écriture des fichiers de résultats

## Remarque importante

Lors de l'exécution de SymetryTest et le calcul de la régression linéaire, il arrive que numpy retourne plusieurs warning.
* RuntimeWarning: invalid value encountered in double\_scalars
* RuntimeWarning: divide by zero encountered in double\_scalars

Cela est due à certains signaux qui sont invalide pour la régression linéaire (1 point).

Pour résoudre cela on déactive les warnings lors de la regressions linéaire.

```python
def SymmetryTest(.....):
    # .....
    np.seterr(divide="ignore")
    np.seterr(invalid="ignore")
    a, b, r_value, p_value, std_err = stats.linregress(sig1, sig2)
    np.seterr(divide="warn")
    np.seterr(divide="ignore")
```
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

--> Rajouter Nan, interpretation des résultats, présentation des documents de sortie (avec screen shot)
