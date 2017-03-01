# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 18:24:10 2017

@author: Matthieu

Flight symmetry analysis
Outil pour l'analyse de la symmetrie d'un vol

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
flight_name = 'E190-E2_20001_0090_29867_54229_request.txt'
path = '../pie_data/'


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

flight_data.reset_data() # Remet les donnees brutes dans data
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
Symmetry
"""
from algorithms.Symmetry import *

error = 0.01 # marge d'erreur relative acceptee (0.01 correspond à 1% de marge)


## With Channels     
result_channel = Symmetry_Channels_One_Flight(flight_data.data,error)

# Analyzes the results (disp number, and if booleans)
res_ch_analyzed = Analyze_results(result_channel, 'channel')
anomalies_channel_couples_names = res_ch_analyzed[0];
anomalies_length_channel_couples = res_ch_analyzed[1];
anomalies_relative_length_channel_couples = anomalies_length_channel_couples/len(flight_data.data)

#..............................................
## With lateral Symmetry 
result_lat = Symmetry_Lateral_One_Flight(flight_data.data,error)

# Analyzes the results (disp number, and if booleans)
res_lat_analyzed = Analyze_results(result_lat, 'lat')
anomalies_lat_couples_names = res_lat_analyzed[0];
anomalies_length_lat_couples = res_lat_analyzed[1];
anomalies_relative_length_lat_couples = anomalies_length_lat_couples/len(flight_data.data)
    
    
#Affichage de l'anomalie la plus importante
s1 = flight_data.data[anomalies_channel_couples_names[0][0]]
s2 = flight_data.data[anomalies_channel_couples_names[0][1]]
s1.plot()
s2.plot()
s3 = flight_data.data[anomalies_lat_couples_names[0][0]]
s4 = flight_data.data[anomalies_lat_couples_names[0][1]]
s3.plot()
s4.plot()   
    

# ecriture du fichier
file_path = "../analyse/1_vol_Matthieu/resultats_symetrie/Resultat1.txt"
write_in_file(file_path, flight_name, anomalies_channel_couples_names, anomalies_relative_length_channel_couples, 1)    
write_in_file(file_path, flight_name, anomalies_lat_couples_names, anomalies_relative_length_lat_couples, 0) 