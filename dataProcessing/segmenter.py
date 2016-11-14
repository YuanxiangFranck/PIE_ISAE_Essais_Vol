# -*- coding: utf-8 -*-
"""
Created on Sat Nov  12 13:25:24 2016

@author: Quentin

Outil pour segmenter les vols
"""

#%%

import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser


#%%

# Chemin relatif vers le fichier txt de données
data_path = ''
# ex : '../../E190-E2_20001_0085_29472_53398-20161004T185141Z/E190-E2_20001_0085_29472_53398/20001_0085_29472_53398_request.txt'
# pour le vol FT53398

# data contient un DataFrame pandas
data = txt_parser(data_path)


# Signaux utilises pour la segmentation
wow = 'WOW_FBK_AMSC1_CHA'
altitude = 'ADSP1 Pressure Altitude (feet)'
altitude_rate = 'ADSP1 Altitude Rate (ft/min)'
calib_air_speed = 'ADSP1 Calibrated Airspeed (knots)'

def get_on_the_ground(data):
    """
    Renvoie la série extraite de data.Time, contenant uniquement les instants lorsque l'avion est au sol
    """
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    return data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)].Time

def get_take_off(data):
    """
    Renvoie la série extraite de data.Time, contenant uniquement les instants lorsque l'avion est en phase de decollage
    """
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    return data.loc[(~on_the_ground) & (altitude_signal < 6000)].Time

def get_climb(data):
    """
    Renvoie la série extraite de data.Time, contenant uniquement les instants lorsque l'avion est en phase de montée
    """
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    alt_rate_signal = data[altitude_rate].iloc[:,0]
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    return data.loc[(~on_the_ground) & (altitude_signal >6000) & (alt_rate_signal > 500)].Time

def get_hold(data):
    """
    Renvoie la série extraite de data.Time, contenant uniquement les instants lorsque l'avion est en phase d'attente
    """
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    alt_rate_signal = data[altitude_rate].iloc[:,0]
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    return data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)].Time

def get_cruise(data):
    """
    Renvoie la série extraite de data.Time, contenant uniquement les instants lorsque l'avion est en phase de croisiere
    """
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    alt_rate_signal = data[altitude_rate].iloc[:,0]
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    return data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)].Time

def get_descent(data):
    """
    Renvoie la série extraite de data.Time, contenant uniquement les instants lorsque l'avion est en phase de descente
    """
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    alt_rate_signal = data[altitude_rate].iloc[:,0]
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    return data.loc[(~on_the_ground) & (alt_rate_signal < -500)].Time