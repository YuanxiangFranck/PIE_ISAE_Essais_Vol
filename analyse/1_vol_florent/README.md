# Analyse d'un vol

Ce fichier README résume le fonctionnement des différents scripts et les avancements obtenus.

L'objectif est de mettre en évidence de façon automatisée des segments temporels anormaux au sein d'un vol, à l'aide de divers descripteurs statistiques. Ces anomalies peuvent être détectées soit de façon visuelle en utilisant des visualisations efficaces, soit en appliquant des algorithmes spécifiques.

**La liste des signaux étudiés est issue du fichier `2016_09_15_Liste_signaux_a_monitorer.xlsx`**

## Analyse des signaux de régulation

Les signaux de régulation sont des grandeurs physiques continues décrivant l'état du système d'air, mesurées par des capteurs. Elles sont commandées par des signaux cible, les signaux *target*. Il est donc possible repérer des comportements anormaux en observant l'écart entre signal et target.

### Heatmap du temps passé hors régulation

### Heatmap des oscillations on/off-regulation

## Analyse des signaux binaires

### Heatmap du nombre de changements d'état

## Détection d'anomalies par OCSVM

