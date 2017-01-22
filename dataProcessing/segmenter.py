# -*- coding: utf-8 -*-
"""
Created on Sat Nov  12 13:25:24 2016

@author: Quentin

Tool to create flight segmentation

TODO : temps passé sur chaque phase sur chaque port
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
    for i in range(len(time_list)-2):
        if time_list[i + 1] != time_list[i] + 1:
            jumps.append((time_list[i],time_list[i+1]))
    if not jumps:
        return [(time_list[0],time_list[-1])] # if time values are continuous, start time = first time, end time = last time
    elif len(jumps)==1:
        return [(time_list[0],jumps[0][0]),(jumps[0][1],time_list[-1])] # If there is one single jump, one segment before the jump, one segment after
    dates = []
    dates.append((time_list[0],jumps[0][0])) # First segment
    for i in range(len(jumps)-1):
        dates.append((jumps[i][1],jumps[i+1][0])) # Intermediate segments
    dates.append((jumps[-1][1],time_list[-1])) # Last segment
    return dates

def segment(data, otg=True, take_off=True, landing=True, climb=True, hold=True, cruise=True, descent=True):
    """
    Extract flight segments and corresponding pressure ports from a dataframe

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
        
    :out: dict of dicts
        keys represent names of segments and values are dictionnaries with pressure ports as keys and lists of tuples (time start,time end) as values
    """
    # Relevant signal names
    wow = 'WOW_FBK_AMSC1_CHA'
    altitude = 'ADSP1 Pressure Altitude (feet)'
    altitude_rate = 'ADSP1 Altitude Rate (ft/min)'
    calib_air_speed = 'ADSP1 Calibrated Airspeed (knots)'
    hp_amsc1_cha = 'HPRSOV_CMD_STATUS_AMSC1_CHA'
    hp_amsc2_cha = 'HPRSOV_CMD_STATUS_AMSC2_CHA'
    hp_amsc1_chb = 'HPRSOV_CMD_STATUS_AMSC1_CHB'
    hp_amsc2_chb = 'HPRSOV_CMD_STATUS_AMSC2_CHB'
    apu_amsc1_cha = 'APU_BLEED_REQUEST_AMSC1_CHA'
    apu_amsc1_chb = 'APU_BLEED_REQUEST_AMSC1_CHB'
    apu_amsc2_cha = 'APU_BLEED_REQUEST_AMSC2_CHA'
    apu_amsc2_chb = 'APU_BLEED_REQUEST_AMSC2_CHB'
    prsov_amsc1_cha = 'PRSOV ACTIVATED_AMSC1_CHA'
    prsov_amsc1_chb = 'PRSOV ACTIVATED_AMSC1_CHB'
    prsov_amsc2_cha = 'PRSOV ACTIVATED_AMSC2_CHA'
    prsov_amsc2_chb = 'PRSOV ACTIVATED_AMSC2_CHB'
    
    # Extraction of relevant signals
    hp_amsc1_cha_signal = data[hp_amsc1_cha]
    hp_amsc2_cha_signal = data[hp_amsc2_cha]
    hp_amsc1_chb_signal = data[hp_amsc1_chb]
    hp_amsc2_chb_signal = data[hp_amsc2_chb]
    apu_amsc1_cha_signal = data[apu_amsc1_cha]
    apu_amsc1_chb_signal = data[apu_amsc1_chb]
    apu_amsc2_cha_signal = data[apu_amsc2_cha]
    apu_amsc2_chb_signal = data[apu_amsc2_chb]
    prsov_amsc1_cha_signal = data[prsov_amsc1_cha]
    prsov_amsc1_chb_signal = data[prsov_amsc1_chb]
    prsov_amsc2_cha_signal = data[prsov_amsc2_cha]
    prsov_amsc2_chb_signal = data[prsov_amsc1_chb]

    hp1 = (hp_amsc1_cha_signal==1) | (hp_amsc1_chb_signal==1)
    hp2 = (hp_amsc2_cha_signal==1) | (hp_amsc2_chb_signal==1)
    apu = (apu_amsc1_cha_signal==1) | (apu_amsc1_chb_signal==1) | (apu_amsc2_cha_signal==1) | (apu_amsc2_chb_signal==1)
    ip1 = (hp1==0) & (apu==0) & ((prsov_amsc1_cha_signal==1) | (prsov_amsc1_chb_signal==1))
    ip2 = (hp2==0) & (apu==0) & ((prsov_amsc2_cha_signal==1) | (prsov_amsc2_chb_signal==1))
    
    
    wow_signal = data[wow]
    altitude_signal = data[altitude]
    cas_signal = data[calib_air_speed]
    delta_cas_signal = data[calib_air_speed].rolling(center = False, window = 120).mean() -  data[calib_air_speed].rolling(center = False, window = 120).mean().shift(1)
    alt_rate_signal = data[altitude_rate].rolling(center = False, window = 120).mean()
    
    # Add filtered values to data
    data["delta_cas_signal"] = delta_cas_signal.fillna(method="bfill")
    data["alt_rate_signal"] = alt_rate_signal.fillna(method="bfill")
    # Compute intervals
    on_the_ground = (wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)
    intervals = dict()
    ports = dict()
    if otg:
        times = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(wow_signal==1) & (cas_signal < 80) & (altitude_signal < 15000) & ip2].Time.values.flatten().tolist()
        intervals['otg'] = cut(times)
        ports['otg'] = dict()
        ports['otg']['hp1'] = cut(times_hp1)
        ports['otg']['hp2'] = cut(times_hp2)
        ports['otg']['apu'] = cut(times_apu)
        ports['otg']['ip1'] = cut(times_ip1)
        ports['otg']['ip2'] = cut(times_ip2)
    if take_off:
        times = data.loc[(cas_signal > 80) & (delta_cas_signal > 0.3) & (altitude_signal < 6000)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(cas_signal > 80) & (delta_cas_signal > 0.3) & (altitude_signal < 6000) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(cas_signal > 80) & (delta_cas_signal > 0.3) & (altitude_signal < 6000) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(cas_signal > 80) & (delta_cas_signal > 0.3) & (altitude_signal < 6000) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(cas_signal > 80) & (delta_cas_signal > 0.3) & (altitude_signal < 6000) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(cas_signal > 80) & (delta_cas_signal > 0.3) & (altitude_signal < 6000) & ip2].Time.values.flatten().tolist()
        intervals['take_off'] = cut(times)
        ports['take_off'] = dict()
        ports['take_off']['hp1'] = cut(times_hp1)
        ports['take_off']['hp2'] = cut(times_hp2)
        ports['take_off']['apu'] = cut(times_apu)
        ports['take_off']['ip1'] = cut(times_ip1)
        ports['take_off']['ip2'] = cut(times_ip2)
    
    if landing:
        times = data.loc[(cas_signal < 150) & (delta_cas_signal < -0.3) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(cas_signal < 150) & (delta_cas_signal < -0.3) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(cas_signal < 150) & (delta_cas_signal < -0.3) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(cas_signal < 150) & (delta_cas_signal < -0.3) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(cas_signal < 150) & (delta_cas_signal < -0.3) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(cas_signal < 150) & (delta_cas_signal < -0.3) & (altitude_signal < 6000) & (alt_rate_signal > -500) & (alt_rate_signal < 0) & ip2].Time.values.flatten().tolist()
        intervals['landing'] = cut(times)
        ports['landing'] = dict()
        ports['landing']['hp1'] = cut(times_hp1)
        ports['landing']['hp2'] = cut(times_hp2)
        ports['landing']['apu'] = cut(times_apu)
        ports['landing']['ip1'] = cut(times_ip1)
        ports['landing']['ip2'] = cut(times_ip2)
    if climb:
        times = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(~on_the_ground) & (altitude_signal > 6000) & (alt_rate_signal > 500) & ip2].Time.values.flatten().tolist()
        intervals['climb'] = cut(times)
        ports['climb'] = dict()
        ports['climb']['hp1'] = cut(times_hp1)
        ports['climb']['hp2'] = cut(times_hp2)
        ports['climb']['apu'] = cut(times_apu)
        ports['climb']['ip1'] = cut(times_ip1)
        ports['climb']['ip2'] = cut(times_ip2)
    if hold:
        times = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(~on_the_ground) & (altitude_signal > 6000) &(altitude_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & ip2].Time.values.flatten().tolist()
        intervals['hold'] = cut(times)
        ports['hold'] = dict()
        ports['hold']['hp1'] = cut(times_hp1)
        ports['hold']['hp2'] = cut(times_hp2)
        ports['hold']['apu'] = cut(times_apu)
        ports['hold']['ip1'] = cut(times_ip1)
        ports['hold']['ip2'] = cut(times_ip2)
    if cruise:
        times = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(~on_the_ground) & (altitude_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500) & ip2].Time.values.flatten().tolist()
        intervals['cruise'] = cut(times)
        ports['cruise'] = dict()
        ports['cruise']['hp1'] = cut(times_hp1)
        ports['cruise']['hp2'] = cut(times_hp2)
        ports['cruise']['apu'] = cut(times_apu)
        ports['cruise']['ip1'] = cut(times_ip1)
        ports['cruise']['ip2'] = cut(times_ip2)
    if descent:
        times = data.loc[(~on_the_ground) & (alt_rate_signal < -500)].Time.values.flatten().tolist()
        times_hp1 = data.loc[(~on_the_ground) & (alt_rate_signal < -500) & hp1].Time.values.flatten().tolist()
        times_hp2 = data.loc[(~on_the_ground) & (alt_rate_signal < -500) & hp2].Time.values.flatten().tolist()
        times_apu = data.loc[(~on_the_ground) & (alt_rate_signal < -500) & apu].Time.values.flatten().tolist()
        times_ip1 = data.loc[(~on_the_ground) & (alt_rate_signal < -500) & ip1].Time.values.flatten().tolist()
        times_ip2 = data.loc[(~on_the_ground) & (alt_rate_signal < -500) & ip2].Time.values.flatten().tolist()
        intervals['descent'] = cut(times)
        ports['descent'] = dict()
        ports['descent']['hp1'] = cut(times_hp1)
        ports['descent']['hp2'] = cut(times_hp2)
        ports['descent']['apu'] = cut(times_apu)
        ports['descent']['ip1'] = cut(times_ip1)
        ports['descent']['ip2'] = cut(times_ip2)
    return intervals,ports

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
    total_duration = data.Time.iloc[-1] - data.Time.iloc[0]
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

    seg,ports = segment(data)
    weights= get_weights(seg,data)
    for key in seg.keys():
        print('Poids du segment {} : {}'.format(key,weights[key]))
        print('Segment {}'.format(key))
        print(seg[key])
        print('#########')
    print(ports['otg']['apu'])
