# Démarche

1. Récupérer les données
2. Récupérer la partie correspondant à la phase
3. Sélectionner des signaux à étudier
4. PCA pour réduire en 2D

# Signaux

* WOW_FBK_AMSC1_CHA
* ADSP1 Pressure Altitude (feet)
* alt_rate_signal
* delta_cas_signal

# Résultat

## hold

On remarque bien que le premier vol (bleu) se distingue des deux autres
A étudier...

## climb

Les données sont globalement très proche mais le vol rouge a ses données moins
groupé que le reste

## Take off / Descent

On peut y reconnaître un pattern qui est suivi par les trois vols.

## Autres

Pas de résultat visible...


# Touts les résultats

![image](segment_climb_features_False.png)

![image](segment_cruise_features_False.png)

![image](segment_descent_features_False.png)

![image](segment_hold_features_False.png)

![image](segment_landing_features_False.png)

![image](segment_otg_features_False.png)

![image](segment_take_off_features_False.png)
