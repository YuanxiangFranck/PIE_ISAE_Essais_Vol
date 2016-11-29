# -*- coding: utf-8 -*-
"""
Created on Sat Nov  12 13:25:24 2016

@author: Quentin

Tool to create flight segmentation

TODO : regarder les recouvrements
"""


import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser

def cut(time_list):
    """
        Create a list of tuples (time start,time end) from a list of discontinuous time values
    """
    if not time_list:
        return []
    jumps = []
    for i in range(len(time_list)-1):
        if time_list[i + 1] != time_list[i] + 1:
            jumps.append((time_list[i],time_list[i+1]))
    if not jumps:
        return [(time_list[0],time_list[-1])] # if time values are continuous, start time = first time, end time = last time
    elif len(jumps)==1:
        return [(time_list[0],jumps[0][0]),(jumps[0][1],time_list[-1])] # If there is one single jump, one segment before the jump, one                                                                        segment after
    dates = []
    dates.append((time_list[0],jumps[0][0])) # First segment
    for i in range(len(jumps)-1):
        dates.append((jumps[i][1],jumps[i+1][0])) # Intermediate segments
    dates.append((jumps[-1][1],time_list[-1])) # Last segment
    return dates

def segment(data, otg=True, take_off=True, landing=True, climb=True, hold=True, cruise=True, descent=True):
    """
    Extract flight segments from a dataframe

    :param data: pd.DataFrame
        flight data
    
    :param otg: boolean
        True to get otg segments
    
    :param take_off: boolean
        True to get take_off segments
    
    :param landing: boolean
        True to get landing segments
    
    :param climb: boolean
        True to get climb segments
        
    :param hold: boolean
        True to get hold segments
    
    :param cruise: boolean
        True to get cruise segments
        
    :param descent: boolean
        True to get descent segments
        
    :out: dict
        keys represent names of segments and values are lists of tuples (time start,time end)
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
    delta_cas_signal = data[calib_air_speed].iloc[:,0].rolling(center = False, window = 30).mean() - data[calib_air_speed].iloc[:,0].rolling(center = False, window = 30).mean().shift(periods=5)
    alt_rate_signal = data[altitude_rate].iloc[:,0].rolling(center = False, window = 120).mean()
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    intervals = dict()
    if otg:
        times = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)].Time.values.flatten().tolist()
        intervals['otg'] = cut(times)
    if take_off: # Ajouter CAS croissante
        times = data.loc[(~on_the_ground) & (cas_signal > 80) & (delta_cas_signal > 0) & (altitude_signal < 6000)].Time.values.flatten().tolist()
        intervals['take_off'] = cut(times)
    if landing:
        times = data.loc[(~on_the_ground) & (cas_signal < 150) & (delta_cas_signal < 0) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0)].Time.values.flatten().tolist()
        intervals['landing'] = cut(times)
    if climb:
        times = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500)].Time.values.flatten().tolist()
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

def get_weights(segments_dict, data):
    """
    Compute the duration of each segment divided by the duration of the flight
        
    :param segments_dict: dict
        Dictionnary containing flight segments, keys represent names of segments, values are lists of tuples (time start,time end)
        
    :param data: pd.DataFrame
        flight data
    
    :out: dict
        keys represent names of segments, values are float representing the time spent in this segment divided by the total duration of the flight
    """
    weights = dict()
    total_duration = data.Time.iloc[-1,0] - data.Time.iloc[0,0]
    for segment in segments_dict.keys():
        weights[segment] = 0
        for time_values in segments_dict[segment]:
            weights[segment] += time_values[1] - time_values[0]
    return {k: v / total_duration for k, v in weights.items()}

if __name__ == "__main__":
    
    # Chemin relatif vers le fichier txt de données
    data_path = '../../Desktop/Articles Liebherr/pie_data/data2.txt'

    # data contient un DataFrame pandas
    data = txt_parser(data_path)
    
    seg = segment(data)
    weights= get_weights(seg,data)
    for key in seg.keys():
        print('Poids du segment {} : {}'.format(key,weights[key]))
        print('Segment {}'.format(key))
        print(seg[key])
        print('#########')