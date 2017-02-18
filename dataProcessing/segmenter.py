# -*- coding: utf-8 -*-
"""
Created on Sat Nov  12 13:25:24 2016

@author: Quentin

Tool to create flight segmentation

TODO : Fichier de configuration, améliorer les filtres
TODO: ajouter des "constantes" en début de fichier au lieu de coder les valeurs en dur
"""


import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser
import matplotlib.pyplot as plt
from pylab import *



def cut(time_list):
    """
        Create a list of tuples (time start,time end) from a list of discontinuous time values
    """
    if not time_list:
        return []

    # Check if there are jumps or not
    jumps = []
    for i in range(len(time_list)-2):
        if time_list[i + 1] != time_list[i] + 1:
            jumps.append((time_list[i],time_list[i+1]))

    if not jumps:
        # if time values are continuous, start time = first time, end time = last time
        return [(time_list[0],time_list[-1])]
    elif len(jumps)==1:
        # If there is one single jump, one segment before the jump, one segment after
        return [(time_list[0],jumps[0][0]),(jumps[0][1],time_list[-1])]

    # Compute dates
    dates = [ (time_list[0], jumps[0][0]) ]  # First segment
    for i in range(len(jumps)-1):
        # Intermediate segments
        dates.append((jumps[i][1], jumps[i+1][0]))
    dates.append((jumps[-1][1], time_list[-1])) # Last segment
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
    Za = 'ADSP1 Pressure Altitude (feet)'
    VZa = 'ADSP1 Altitude Rate (ft/min)'
    CAS = 'ADSP1 Calibrated Airspeed (knots)'
    HP_controller1_chA_cmd = 'HPRSOV_CMD_STATUS_AMSC1_CHA'
    HP_controller2_chA_cmd = 'HPRSOV_CMD_STATUS_AMSC2_CHA'
    HP_controller1_chB_cmd = 'HPRSOV_CMD_STATUS_AMSC1_CHB'
    HP_controller2_chB_cmd = 'HPRSOV_CMD_STATUS_AMSC2_CHB'
    APU_controller1_chA_cmd = 'APU_BLEED_REQUEST_AMSC1_CHA'
    APU_controller1_chB_cmd = 'APU_BLEED_REQUEST_AMSC1_CHB'
    APU_controller2_chA_cmd = 'APU_BLEED_REQUEST_AMSC2_CHA'
    APU_controller_2_chB_cmd = 'APU_BLEED_REQUEST_AMSC2_CHB'
    PRSOV_controller1_chA_cmd = 'PRSOV ACTIVATED_AMSC1_CHA'
    PRSOV_controller1_chB_cmd = 'PRSOV ACTIVATED_AMSC1_CHB'
    PRSOV_controller2_chA_cmd = 'PRSOV ACTIVATED_AMSC2_CHA'
    PRSOV_controller2_chB_cmd = 'PRSOV ACTIVATED_AMSC2_CHB'

    # Extraction of relevant signals
    HP_controller1_chA_cmd_signal = data[HP_controller1_chA_cmd]
    HP_controller2_chA_cmd_signal = data[HP_controller2_chA_cmd]
    HP_controller1_chB_cmd_signal = data[HP_controller1_chB_cmd]
    HP_controller2_chB_cmd_signal = data[HP_controller2_chB_cmd]
    APU_controller1_chA_cmd_signal = data[APU_controller1_chA_cmd]
    APU_controller1_chB_cmd_signal = data[APU_controller1_chB_cmd]
    APU_controller2_chA_cmd_signal = data[APU_controller2_chA_cmd]
    APU_controller_2_chB_cmd_signal = data[APU_controller_2_chB_cmd]
    PRSOV_controller1_chA_cmd_signal = data[PRSOV_controller1_chA_cmd]
    PRSOV_controller1_chB_cmd_signal = data[PRSOV_controller1_chB_cmd]
    PRSOV_controller2_chA_cmd_signal = data[PRSOV_controller2_chA_cmd]
    PRSOV_controller2_chB_cmd_signal = data[PRSOV_controller2_chB_cmd]

    hp1 = (HP_controller1_chA_cmd_signal==1) | (HP_controller1_chB_cmd_signal==1)
    hp2 = (HP_controller2_chA_cmd_signal==1) | (HP_controller2_chB_cmd_signal==1)
    apu = (APU_controller1_chA_cmd_signal==1) | (APU_controller1_chB_cmd_signal==1) | (APU_controller2_chA_cmd_signal==1) | (APU_controller_2_chB_cmd_signal==1)
    ip1 = (hp1==0) & (apu==0) & ((PRSOV_controller1_chA_cmd_signal==1) | (PRSOV_controller1_chB_cmd_signal==1))
    ip2 = (hp2==0) & (apu==0) & ((PRSOV_controller2_chA_cmd_signal==1) | (PRSOV_controller2_chB_cmd_signal==1))
    no_bleed = ~(hp1|hp2|ip1|ip2|apu)


    wow_signal = data[wow]
    Za_signal = data[Za]
    CAS_signal = data[CAS]
    WINDOW_CAS = 120
    delta_CAS_signal = data[CAS].rolling(center = False, window = WINDOW_CAS).mean() -  data[CAS].rolling(center = False, window = WINDOW_CAS).mean().shift(1)
    alt_rate_signal = data[VZa].rolling(center = False, window = 120).mean()


    # Add filtered values to data
    data["delta_CAS_signal"] = delta_CAS_signal.fillna(method="bfill")
    data["alt_rate_signal"] = alt_rate_signal.fillna(method="bfill")

    is_taking_off_signal = data["delta_CAS_signal"].copy()
    is_landing_signal = data["delta_CAS_signal"].copy()
    is_descending_signal = data["alt_rate_signal"].copy()

    # Hysteresis to detect take_off phases
    triggered = False
    for i in range(len(data["delta_CAS_signal"])):
        if data["delta_CAS_signal"][i] > 0.2:
            triggered = True
        if triggered:
            if data["delta_CAS_signal"][i] < -0.1:
                triggered = False
                is_taking_off_signal[i] = 0
            else:
                is_taking_off_signal[i] = 1
        else:
            is_taking_off_signal[i] = 0

    # Hysteresis to detect landing phases
    triggered = False
    for i in range(len(data["delta_CAS_signal"])):
        if data["delta_CAS_signal"][i] < - 0.2:
            triggered = True
        if triggered:
            if data["delta_CAS_signal"][i] > 0.1:
                triggered = False
                is_landing_signal[i] = 0
            else:
                is_landing_signal[i] = 1
        else:
            is_landing_signal[i] = 0


    # Hysteresis to detect descent
    triggered = False
    for i in range(len(data["alt_rate_signal"])):
        if data["alt_rate_signal"][i] < - 0.1:
            triggered = True
        if triggered:
            if data["alt_rate_signal"][i] > 0.5:
                triggered = False
                is_descending_signal[i] = 0
            else:
                is_descending_signal[i] = 1
        else:
            is_descending_signal[i] = 0


    # Add hysteresis to data
    data['is_taking_off'] = is_taking_off_signal
    data['is_landing'] = is_landing_signal
    data['is_descending'] = is_descending_signal

    # Compute intervals
    on_the_ground = (wow_signal==1) & (CAS_signal < 80) & (Za_signal < 15000)
    not_on_the_ground = np.logical_not(on_the_ground)
    ports_idx = {"hp1": hp1, "hp2": hp2, "apu": apu,
                 "ip1": ip1, "ip2": ip2, "no bleed": no_bleed}
    segments = {}
    if otg:
        segments["otg"] = on_the_ground
    if take_off:
        segments["take_off"] = (CAS_signal > 80) & (is_taking_off_signal==1) & (Za_signal < 6000) & (~on_the_ground)
    if landing:
        segments["landing"]  = (CAS_signal < 150) & (is_landing_signal==1) & (Za_signal < 6000) & (alt_rate_signal > -500) & (~on_the_ground)
    if climb:
        segments["climb"]    = (~on_the_ground) & (Za_signal > 6000) & (alt_rate_signal > 500)
    if hold:
        segments["hold"]     = (~on_the_ground) & (Za_signal > 6000) & (Za_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)
    if cruise:
        segments["cruise"]   = (~on_the_ground) & (Za_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)
    if descent:
        segments["descent"]  = (~on_the_ground) & (alt_rate_signal < -500)

    # Compute segments and ports
    intervals = {}
    ports = {}
    ports_full_flight = {}
    for segment_name, segment_idx in segments.items():
        times = data.loc[segment_idx].Time.values.flatten().tolist()
        intervals[segment_name] = cut(times)
        ports[segment_name] = {}
        for port_name, port_idx in ports_idx.items():
            time_on_port = data.loc[segment_idx & port_idx].Time.values.flatten().tolist()
            ports[segment_name][port_name] = cut(time_on_port)

    ports_full_flight['hp1'] = cut(data.loc[hp1].Time.values.flatten().tolist())
    ports_full_flight['hp2'] = cut(data.loc[hp2].Time.values.flatten().tolist())
    ports_full_flight['ip1'] = cut(data.loc[ip1].Time.values.flatten().tolist())
    ports_full_flight['ip2'] = cut(data.loc[ip2].Time.values.flatten().tolist())
    ports_full_flight['apu'] = cut(data.loc[apu].Time.values.flatten().tolist())
    ports_full_flight['no bleed'] = cut(data.loc[no_bleed].Time.values.flatten().tolist())
    return intervals, ports, ports_full_flight


def tuples_to_durations(dic):
    """
        Convert a dictionnary containing lists of tuples (t_start, t_end) as values into the same dictionnary with durations
        as values

        :param dic: dict
            Dictionnary with lists of tuples (t_start, t_end) as values
        :out dict
            Dictionnary with lists of durations as values
    """
    durations = {}
    for key, time_values in dic.items():
        durations[key] = sum(end-start for start, end in time_values)
    return durations

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

def seg_durations(segments_dict, data):
    """
    Return the duration of each segment
    """
    weights = dict()
    for segment in segments_dict.keys():
        weights[segment] = 0
        for time_values in segments_dict[segment]:
            weights[segment] += time_values[1] - time_values[0]
    return {k: v  for k, v in weights.items()}

def get_weights_ports(ports_dict, data):
    """
    For each segment, compute the duration on each pressure port

    :param ports_dict: dict
        Dictionnary of dictionnary

    :param data: pd.DataFrame
        flight data

    :out: dict of dicts

    """
    weights_ports = dict()
    seg,_,_ = segment(data)
    durations = seg_durations(seg,data)  # durations of the segments
    for each_segment in ports_dict.keys():
        duration = durations[each_segment]
        weights_ports[each_segment] = dict()
        for port in ports_dict[each_segment].keys():
            weights_ports[each_segment][port] = 0
            for time_values in ports_dict[each_segment][port]:
                weights_ports[each_segment][port] += time_values[1] - time_values[0]
            if duration != 0: weights_ports[each_segment][port] = weights_ports[each_segment][port]/duration
    return weights_ports


def plot_seg(data):
    """
    Plot a pie chart of the percentage of time spent on each segment

    :param weights: dict
        Dictionnary with segment names as keys and weight as values (see get_weights to compute this dictionnary)
    """
    seg,_,_= segment(data)
    weights = get_weights(seg, data)
    figure(1, figsize=(10,10))
    labels = list(weights.keys())
    fracs = [weights[key] for key in labels]
    if sum([weight for weight in fracs]) < 1:
        fracs.append(1 - sum([weight for weight in fracs]))
        labels.append('no segment')
    colors = ['gold', 'yellowgreen', 'orange', 'lightskyblue','dodgerblue','indianred','orchid','red'][:len(fracs)]
    pie(fracs,labels=labels,colors=colors,autopct='%1.1f%%')
    title('Temps passé dans chaque phase, en pourcentage de la durée du vol', bbox={'facecolor':'0.8', 'pad':5})
    draw()

def plot_ports_seg(data):
    _,ports,_ = segment(data)
    for each_segment in ports.keys():
        ports[each_segment] = tuples_to_durations(ports[each_segment])
    f, axarr = plt.subplots(2, 7,figsize=(23,7))
    f.suptitle('Utilisation des ports selon chaque phase',bbox={'facecolor':'0.8', 'pad':5})
    j = 0
    for each_segment in ports:
        labels = ports[each_segment].keys()  # pressure ports names
        labels_1 = [label for label in labels if label[-1]=='1'] + ['apu','no bleed'] # left pressure ports + apu
        labels_2 = [label for label in labels if label[-1]=='2'] + ['apu','no bleed'] # right pressure ports + apu
        fracs_1 = [ports[each_segment][key] for key in labels_1]
        fracs_2 = [ports[each_segment][key] for key in labels_2]
        colors = ['gold', 'yellowgreen', 'orange', 'lightskyblue','dodgerblue','indianred','orchid'][:len(labels)]
        axarr[0, j].pie(fracs_1,labels=labels_1,colors=colors,autopct='%1.1f%%')
        axarr[0, j].set_title('{} côté 1'.format(each_segment), bbox={'facecolor':'0.8', 'pad':5})
        axarr[1, j].pie(fracs_2,labels=labels_2,colors=colors,autopct='%1.1f%%')
        axarr[1, j].set_title('{} côté 2'.format(each_segment), bbox={'facecolor':'0.8', 'pad':5})
        j = (j+1)%7
    plt.show()

def plot_ports_sides(data):
    _,_,ports_full_flight = segment(data)
    #flight_duration = data.Time.iloc[-1] - data.Time.iloc[0]
    ports_durations = tuples_to_durations(ports_full_flight)
    #for port in ports_durations.keys():
    #    ports_durations[port] /= flight_duration
    f, axarr = plt.subplots(1, 2,figsize=(20,10))
    labels = ports_durations.keys()  # pressure ports names
    labels_1 = [label for label in labels if label[-1]=='1'] + ['apu','no bleed'] # left pressure ports + apu
    labels_2 = [label for label in labels if label[-1]=='2'] + ['apu','no bleed'] # right pressure ports + apu
    fracs_1 = [ports_durations[key] for key in labels_1]
    fracs_2 = [ports_durations[key] for key in labels_2]
    colors = ['gold', 'yellowgreen', 'orange', 'lightskyblue','dodgerblue','indianred','orchid'][:len(labels)]
    axarr[0].pie(fracs_1,labels=labels_1,colors=colors,autopct='%1.1f%%')
    axarr[0].set_title('côté 1', bbox={'facecolor':'0.8', 'pad':5})
    axarr[1].pie(fracs_2,labels=labels_2,colors=colors,autopct='%1.1f%%')
    axarr[1].set_title('côté 2', bbox={'facecolor':'0.8', 'pad':5})
    plt.show()

def plot_ports(data):
    """
    Plot a pie chart of the percentage of time spent on each pressure port

    :param ports_full_flight: dict
        Dictionnary with ports names as keys and listes of tuples (t_start,t_end) as values

    :param data
        pandas df
    """
    _,_,ports_full_flight = segment(data)
    flight_duration = data.Time.iloc[-1] - data.Time.iloc[0]
    ports_durations = tuples_to_durations(ports_full_flight)
    # Convert durations on each port into percentage of the flight duration
    for port in ports_durations.keys():
        ports_durations[port] /= flight_duration
    figure(1, figsize=(10,10))
    labels = ports_durations.keys()
    fracs = [ports_durations[key] for key in labels]
    colors = ['gold', 'yellowgreen', 'orange', 'lightskyblue','dodgerblue','indianred','orchid'][:len(labels)]
    pie(fracs,labels=labels,colors=colors,autopct='%1.1f%%')
    title('Temps passé sur chaque port, en pourcentage de la durée du vol', bbox={'facecolor':'0.8', 'pad':5})
    show()



if __name__ == "__main__":

    # Chemin relatif vers le fichier txt de données
    data_path = '../../Desktop/Articles Liebherr/pie_data/data2.txt'


    # data contient un DataFrame pandas
    data = txt_parser(data_path)

    #for key in seg.keys():
    #    print('Poids du segment {} : {}'.format(key,weights[key]))
    #    print(seg[key])
    #    print('#########')
    #print(ports['otg'])
    #weights_ports = get_weights_ports(ports,data)
    #print(weights_ports)

    plot_seg(data)
    plot_ports_seg(data)
    plot_ports_sides(data)
    plot_ports(data)
