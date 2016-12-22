# -*- coding: utf-8 -*-
"""
Created on Wed Nov  23 2016

@author: Remy

Template pour trier le signal
"""

#%%

import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser
import algorithms.NNeighbor as NN 


#%%

"""
Vol XXXXX
(préciser le numéro du vol étudié)

"""

## 1. Chargement du fichier de données

# Chemin relatif vers le fichier txt de données
data_path = '../../pie_data/data1.txt'
# ex : '../../E190-E2_20001_0085_29472_53398-20161004T185141Z/E190-E2_20001_0085_29472_53398/20001_0085_29472_53398_request.txt'
# pour le vol FT53398

# data contient un DataFrame pandas
data = txt_parser(data_path)

## 2. Lecture d'un signal

# nom du signal (ex: BLEED_OUT_TEMP_AMSC1_CHA)
signal_name = 'BLEED_OUT_TEMP_AMSC1_CHA'

# renvoie la série temporelle sous forme de Serie pandas
signal = data[signal_name].iloc[:,0] # on prend toutes les lignes de la 1e colonne

#renvoie l'unité physique du signal
unit = data[signal_name].columns[0]
#ex : 'DGC' pour des degrés Celsius

#res = NN.NearestNeighbor(signal,20,10)

print (signal)
"""
Have fun!
Vous pouvez maintenant appliquer tous les algos que vous voulez
sur la série temporelle 'signal' !
"""
                                                                                                                                                                                                                                                                                               