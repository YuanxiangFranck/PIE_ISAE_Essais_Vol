# Clustering des données brut pour chaque phase de vol

**ATTENTION:**
Pour l'instant le segmenteur de vol n'est pas complètement
paramétré ce qui a pour conséquence que certains résultat présent peuvent être
faussé.


Le but pour l'instant et d'implémenter toute la démarche pour pouvoir la
exécuter plus tard si nécessaire
Le second objectif est de commencé à se familiariser avec les données en les manipulant.


## Démarche

1. Récupérer les données
2. Récupérer la partie correspondant au pas de temps
3. Sélectionner des signaux à étudier
4. [Appliquer des features]
5. PCA pour réduire en 2D
6. Afficher les résultats + conclusion

## Étude basique

But créer une routine de clustering pour l'analyse de n vol
Dans un premier temps on travaille avec les données brut pour mieux se les approprier.

On calculera les features sur chaque fenêtre de temps puis utiliser une PCA pour
pouvoir les afficher.

Cela dans l'objectif de trouver certains pattern dans les différentes phases de
vol et chercher les différences entre les vols.

### Clustering des données brut

On remarque que dans la phase _hold_ un des vol se distingue clairement des autres.
On aperçoit aussi un semblant de pattern dans les phases __Take off__ et __Descent__

Détails + images dans [/basic_raw](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/n_vol_franck/basic_raw/)

### Clustering des données brut + lissage

A ce stage le segmenter ne distingue n'a trouvé de phase 'cruise' que dans un
vol donc ces données sont inutiles.

Image dans dans [/basic_raw](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/n_vol_franck/basic_filtered/)

## Application de features

Features:

* min
* max
* mean
* covariance

### Sans fenêtre glissante

Pas assez de données pour être exploitable

Image dans dans [/basic_raw](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/n_vol_franck/no_sl_window/)

### Avec fenêtre glissante

#### Features indépendante

Sur chaque segment de la fenêtre glissante on applique les différentes features
sélectionnées.
Puis on applique la PCA sur les 4 signaux.

Chaque point représente une fenêtre de temps sur lequel on a appliqué une features.

Image dans dans [/basic_raw](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/n_vol_franck/sl_win/)

#### Features regroupé par PCA


On applique la PCA sur les 4 signaux * les features

Chaque point représente donc les signaux + features sur chaque fenêtre de temps.


Image dans dans [/basic_raw](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/n_vol_franck/pca_donne_features/)
