# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 18:24:10 2017

@author: Florent

Script pour l'analyse des signaux de régulation d'un vol

Visualisation d'une feature sur différents 
segments temporels sur une heatmap
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

flight_name = 'E190-E2_20001_0089_29800_54082_request.txt'
path = '../../data/'

whole_flight = load_flight(path+flight_name)

flight_data = SignalData(whole_flight)

#%%
"""
Segmentation et sélection de la phase de vol
* all : garder toutes les phases
* climb/cruise/descent/hold/landing/otg/take_off
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
"""

n_samples = 20

sl_w = len(flight_data.data)//n_samples
sl_s = sl_w

"""
On vérifie si chaque portion la phase étudiée est bien
supérieure à la fenêtre de temps (cela empêche le bon 
fonctionnement de la fonction "idx2date" et cela n'a
pas de sens d'avoir une fenêtre plus grande que la phase
elle-même)
"""
if phase != 'all':
    assert(min([date[1]-date[0] \
                for date in flight_data.flight_segments[phase]]) \
            > sl_w)
    
samples = extract_sl_window_delta(flight_data.data, signal_names_regul, \
                                  target_names_regul, sl_w, sl_s)

#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

features = ['percent_time_over_threshold']
threshold = 0.1

feature_matrix = get_feature_matrix(samples, features, normalized=False, \
                                    threshold=threshold)

#%%
"""
Analyse
Heatmap
"""

import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['figure.figsize']=(10,10)
if phase != 'all':
    time_labels = [idx2date(flight_data.flight_segments[phase],\
                           idx,sl_w,sl_s) for idx in range(len(samples))]
else:
    origin = flight_data.data.Time.iloc[0]
    end = flight_data.data.Time.iloc[-1]
    time_labels = [idx2date([(origin,end)],\
                           idx,sl_w,sl_s) for idx in range(len(samples))]
                                         
sns.heatmap(feature_matrix.T, xticklabels = time_labels, \
            yticklabels=signal_names_regul)
plt.title('- Percent time over threshold -\n'\
          'Flight : {} / Phase : {}\n'
          'Data : relative error between regulation and target signals\n'\
          'Threshold : {} %\n'\
          'Time window : {} s'.format(flight_name,phase,threshold*100, sl_w))