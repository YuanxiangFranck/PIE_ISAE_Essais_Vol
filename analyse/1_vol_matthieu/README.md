# Détection d'anomalies sur un vol


**Objectif :**
Appliquer des algorithmes pour mettre en évidence la présence de signaux anormaux parmis les milliers de mesures disponibles. Une première idée est tout d'abord de comparer les signaux qui sont censés être égaux. C'est normalement le cas pour les signaux sur les channels A et B, ou encore sur les mesures physiques qui doivent normalement être symétriques par construction de l'avion. 

## Données

On dispose donc des données d'un seul vol, parmi ceux à notre disposition.
**Script :** [Symmetry.py](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/algorithms/Symmetry.py)

## Tests d'égalité de deux signaux

Afin de détecter les signaux qui diffèrent, je procède simplement comme suit :
* L'utilisateur choisit une valeur de l'*erreur* acceptable.
* Le test d'égalité est positif si à tout instant, la différence relative entre les deux signaux est inférieure à l'erreur entrée par l'utilisateur

## Egalité supposée des signaux

Comme dit précédemment, l'idée est d'utiliser la redondance et les symétries de l'avion pour détecter les anomalies.

###Signaux égaux par symétrie
Si je ne m'abuse, les signaux représentant les mêmes mesures physiques sur les deux côtés droite/gauche de l'avion présentent dans leur nom les caractères : **AMSC1** ou **AMSC2**. Il conviendra alors de tester s'ils diffèrent. Je ne l'ai pas encore implémenté. 

###Signaux égaux par redondance
Dans ce cas de figure, les signaux des channels A et B, mentionnés à la fin de leur nom par les caractères **CHA** ou **CHB**, doivent être égaux. Ce test a été codé.

Par exemple, pour le vol **data1**, lancer la fonction *Symmetry_One_Flight* avec en argument une erreur de 1 redonnera le nom de tous les signaux supposés égaux mais qui diffèrent avec une erreur relative d'au moins 100%, ainsi que les indices temporelles correspondants aux différences. Dans cet exemple, l'algorithme en trouve 208, parmi lesquels le couple **ZONE1_TAV_DRIV_F_AMSC1_CHA** et **ZONE1_TAV_DRIV_F_AMSC1_CHB**. L'affichage de ces deux signaux montre bien qu'il y a une différence.

![image](redondance_anomaly.png)

