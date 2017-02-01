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
"""
flight_name = 'E190-E2_20001_0083_29106_52495_request.txt'
path = '../../data/'

whole_flight = load_flight(path+flight_name)

flight_data = SignalData(whole_flight)

#%%
"""
Segmentation et sélection de la phase de vol
* all : garder toutes les phases
* climb/cruise/descent/hold/landing/otg/take_off
"""

"""
Example
"""
phase = 'all'

flight_data.reset_data()
if phase != 'all':
    flight_data.apply_flight_segmentation(phase)

#%%
"""
Extraction des signaux par sliding window
* n_samples : nombre de segments à découper par sliding window
* vous pouvez aussi fixer manuellement sl_w et sl_s
* en cas d'utilisation de deltas entre signaux, vous pouvez
  préciser si l'écart doit être relatif/absolu pour chaque signal,
  à l'aide de la liste delta_type
"""

"""
Example
"""
n_samples = 20

sl_w = len(flight_data.data)//n_samples
sl_s = sl_w

samples = extract_sl_window(flight_data.data, signal_names_regul, \
                            sl_w, sl_s)
#delta_type = ['rel'] * len(signal_names_regul)
#samples = extract_sl_window_delta(flight_data.data, signal_names_regul, \
#                                  target_names_regul, sl_w, sl_s, delta_type)

#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

"""
Example
"""
features = ['percent_time_over_threshold']
threshold = 0.1

feature_matrix = get_feature_matrix(samples, features, normalized=False, \
                                    threshold=threshold)

#%%
"""
Algorithmes, visualisations
* METTRE ICI CE QUE VOUS VOULEZ
"""
