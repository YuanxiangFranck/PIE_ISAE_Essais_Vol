# Analyse d'un vol

Ce fichier README résume le fonctionnement des différents scripts et les avancements obtenus.

L'objectif est de mettre en évidence de façon automatisée des segments temporels anormaux au sein d'un vol, à l'aide de divers descripteurs statistiques. Ces anomalies peuvent être détectées soit de façon visuelle en utilisant des visualisations efficaces, soit en appliquant des algorithmes spécifiques.

*La liste des signaux étudiés est issue du fichier `2016_09_15_Liste_signaux_a_monitorer.xlsx`*.

## Analyse des signaux de régulation

Les signaux de régulation sont des grandeurs physiques continues décrivant l'état du système d'air, mesurées par des capteurs. Elles sont commandées par des signaux cible, les signaux *target*. Il est donc possible repérer des comportements anormaux en observant l'écart entre signal et target.

### Heatmap du temps passé hors régulation

Le vol est découpé en segments temporels de durée fixe. Pour chaque signal et chaque segment, on calcule une feature, i.e. un descripteur statistique ou physique de la donnée. On représente cette valeur sur une matrice appelée *heatmap*. Une couleur plus foncée signifie en général une valeur plus élevée (l'échelle est représentée sur l'axe sur la droite de la figure). Le feature étudiée ici est le pourcentage de temps passé hors régulation.

**Percent time off-regulation** :
Nombre de pas de temps où l'écart absolu ou relatif entre un signal et sa target dépasse un certain seuil absolu ou relatif, divisé par le nombre de pas de temps du segment temporel. La valeur de ce seuil est différente pour chaque signal et spécifiée dans le fichier ![target_precisions.csv](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/algorithms/target_precisions.csv).

On obtient une visualisation semblable à la figure ci-dessous :

![Exemple de heatmap](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/1_vol_florent/0085_29472_53398/hm_regul_target_percent_time_off_regulation_all_ex.png)

Sur cette heatmap, on remarque par exemple que sur ce vol, le premier signal (`ACS_MIX_TEMP_AMSC1_CHA`) est éloigné de sa cible sur les intervalles de temps [44420, 44661] et [45384, 46607]. Vérifions ce constat sur la courbe du signal et de sa target :

![Exemple de comportement anormal](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/analyse/1_vol_florent/0085_29472_53398/ACS_MIX_TEMP_AMSC1_CHA_ex.png)

### Heatmap des oscillations on/off-regulation

## Analyse des signaux binaires

### Heatmap du nombre de changements d'état

## Détection d'anomalies par OCSVM

