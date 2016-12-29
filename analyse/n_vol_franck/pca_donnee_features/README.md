# Démarche

1. Récupérer les données
2. Récupérer la partie correspondant à la phase
3. Sélectionner des signaux à étudier
4. Application des features
5. PCA pour réduire en 2D

# Signaux

* WOW_FBK_AMSC1_CHA
* ADSP1 Pressure Altitude (feet)
* alt_rate_signal
* delta_cas_signal

# Features:

* min
* max
* mean
* covariance

# Résultat

On applique la PCA sur les 4 signaux * les features

Chaque point représente donc les signaux + features sur chaque fenêtre de temps.

### hold

Vol bleu se distingue des autres

### Descent / landing

Pattern reconnaissable.

### otg / landing

Semblant de pattern

# Touts les résultats

![image](segment_climb_features_mean_min_max_covariance.png)

![image](segment_cruise_features_mean_min_max_covariance.png)

![image](segment_descent_features_mean_min_max_covariance.png)

![image](segment_descent_features_mean_min_max_covariance-1.png)

![image](segment_hold_features_mean_min_max_covariance.png)

![image](segment_landing_features_mean_min_max_covariance.png)

![image](segment_otg_features_mean_min_max_covariance.png)

![image](segment_take_off_features_mean_min_max_covariance.png)
