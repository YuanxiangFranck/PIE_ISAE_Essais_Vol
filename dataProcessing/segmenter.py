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

def cut(time_list):
    """
        Create a list of tuples (time start,time end) from a list of discontinuous time values
    """
    if not time_list:
        return []
    else :
        jumps = []
        for i in range(len(time_list)-1):
            if time_list[i + 1] != time_list[i] + 1:
                jumps.append((time_list[i],time_list[i+1]))
        if not jumps:
            return [(time_list[0],time_list[-1])] # if time values are continuous, start time = first time, end time = last time
        elif len(jumps)==1:
            return [(time_list[0],jumps[0][0]),(jumps[0][1],time_list[-1])] # If there is one single jump, one segment before the jump, one                                                                         segment after
        else :
            dates = []
            dates.append((time_list[0],jumps[0][0])) # First segment
            for i in range(len(jumps)-1):
                dates.append((jumps[i][1],jumps[i+1][0])) # Intermediate segments
            dates.append((jumps[-1][1],time_list[-1])) # Last segment
            return dates

def segment(data, otg=True, take_off=True, climb=True, hold=True, cruise=True, descent=True):
    """
    Extract flight segments from a dataframe

    :param data: pd.DataFrame
        flight data
    
    :param otg: boolean
        True to get otg segments
    
    :param take_off: boolean
        True to get take_off segments
    
    :param climb: boolean
        True to get climb segments
        
    :param hold: boolean
        True to get hold segments
    
    :param cruise: boolean
        True to get cruise segments
        
    :param descent: boolean
        True to get descent segments
        
    :out: dict
        keys represent names of segments and values are lists of tuples(time start,time end)
    """
    # Relevant signal names
    wow = 'WOW_FBK_AMSC1_CHA'
    altitude = 'ADSP1 Pressure Altitude (feet)'
    altitude_rate = 'ADSP1 Altitude Rate (ft/min)'
    calib_air_speed = 'ADSP1 Calibrated Airspeed (knots)'
    
    # Extraction of relevant signals
    wow_signal = data[wow].iloc[:,0]
    altitude_signal = data[altitude].iloc[:,0]
    cas_signal = data[calib_air_speed].iloc[:,0]
    alt_rate_signal = data[altitude_rate].iloc[:,0]
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)i
    intervals = dict()
    if otg:
        times = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)].Time.values.flatten().tolist()
        intervals['otg'] = cut(times)
    if take_off:
        times = data.loc[(~on_the_ground) & (altitude_signal < 6000)].Time.values.flatten().tolist()
        intervals['take_off'] = cut(times)
    if climb:
        times = data.loc[(~on_the_ground) & (altitude_signal >6000) & (alt_rate_signal > 500)].Time.values.flatten().tolist()
        intervals['climb'] = cut(times)
    if hold:
        times = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)].Time.values.flatten().tolist()
        intervals['hold'] = cut(times)
    if cruise:
        times = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)].Time.values.flatten().tolist()
        intervals['cruise'] = cut(times)
    if descent:
        times = data.loc[(~on_the_ground) & (alt_rate_signal < -500)].Time.values.flatten().tolist()
        intervals['descent'] = cut(times)
    return intervals