# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 18:24:10 2017

@author: Florent

Flight analysis
Outil pour l'analyse d'un vol
* calcul de features
* application d'algorithmes
* visualisation
"""

#%%
"""
Import des fonctions utiles à l'analyse
"""
from flight_analysis_fun import *

#%%
"""
Import des noms de signaux
* signal_names_regul : signaux de régulation
* target_names_regul : cibles des signaux de régulation
* signal_names_for_segmentation : signaux utilisés pour la segmentation
* signal_names_bin : signaux binaires
"""
from signal_names import signal_names_regul, target_names_regul

#%%
"""
Sélection et chargement du vol
* modifier le path relatif si besoin
"""

"""
Example

flight_name = 'E190-E2_20001_0085_29472_53398_request.txt'
path = '../../data/'

flight_data = load_flight(path+flight_name)
"""


#%%
"""
Extraction des signaux par sliding window
"""

"""
Example

samples = extract_sl_window_delta(flight_data, signal_names_regul, \
                                  target_names_regul, 60, 30)
"""


#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

"""
Example

features = ['time_over_threshold','mean_crossings']
threshold = 0.1
feature_matrix = get_feature_matrix(samples, features, normalized=True, \
                                    threshold=threshold)
"""


#%%
"""
Algorithmes, visualisations
* TO DO
"""
