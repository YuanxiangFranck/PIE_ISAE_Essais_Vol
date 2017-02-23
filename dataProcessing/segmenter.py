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
import matplotlib.pyplot as plt
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter_utils import hysteresis, tuples_to_durations, get_weights, cut

plot_colors = ['gold', 'yellowgreen', 'orange', 'lightskyblue', 'dodgerblue',
              'indianred', 'orchid']

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
    time_step = 1 


    wow_signal = data[wow]
    Za_signal = data[Za]
    CAS_signal = data[CAS]
    window_CAS = int(30/time_step)
    window_VZa = int(40/time_step)
    delta_CAS_signal = data[CAS].rolling(center = False, window = window_CAS).mean() -  data[CAS].rolling(center = False, window = window_CAS).mean().shift(1)
    alt_rate_signal = data[VZa].rolling(center = False, window = window_VZa).mean()


    # Add filtered values to data
    data["delta_CAS_signal"] = delta_CAS_signal.fillna(method="bfill")
    data["alt_rate_signal"] = alt_rate_signal.fillna(method="bfill")

    # Add hysteresis to data
    is_taking_off_signal = hysteresis(data["delta_CAS_signal"], 0, 1)
    is_landing_signal = hysteresis(-data["delta_CAS_signal"], -1, .1)
    data['is_taking_off'] = is_taking_off_signal
    data['is_landing']    = is_landing_signal
   
    # Compute intervals
    on_the_ground = (wow_signal==1) & (CAS_signal < 80) & (Za_signal < 15000)
    not_on_the_ground = ~(on_the_ground)
    ports_idx = {"hp1": hp1, "hp2": hp2, "apu": apu,
                 "ip1": ip1, "ip2": ip2, "no bleed": no_bleed}

    segments = {}
    if otg:
        segments["otg"] = on_the_ground
    if take_off:
        segments["take_off"] = not_on_the_ground & (Za_signal < 6000)  & (CAS_signal > 80) & is_taking_off_signal
    if landing:
        segments["landing"]  = not_on_the_ground & (Za_signal < 6000)  & (alt_rate_signal > -500) & (alt_rate_signal < 0) & (CAS_signal < 150) & is_landing_signal
    if climb:
        segments["climb"]    = not_on_the_ground & (Za_signal >= 6000) & (alt_rate_signal > 500)
    if hold:
        segments["hold"]     = not_on_the_ground & (Za_signal >= 6000) & (Za_signal < 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)
    if cruise:
        segments["cruise"]   = not_on_the_ground & (Za_signal > 25000) & (alt_rate_signal > -500) & (alt_rate_signal < 500)
    if descent:
        segments["descent"]  = not_on_the_ground & (alt_rate_signal < -500)

    # Compute segments and ports
    intervals = {}
    ports = {}
    ports_full_flight = {}
    for segment_name, segment_idx in segments.items():
        intervals[segment_name] = cut(data.Time[segment_idx])
        ports[segment_name] = {}
        for port_name, port_idx in ports_idx.items():
            time_on_port = data.Time[segment_idx & port_idx]
            ports[segment_name][port_name] = cut(time_on_port)

    # Compute ports_full_fight
    for port_name, port_idx in ports_idx.items():
        ports_full_flight[port_name] = cut(data.Time[port_idx])
    return intervals, ports, ports_full_flight




def plot_seg(data):
    """
    Plot a pie chart of the percentage of time spent on each segment

    :param data: pd.DataFrame
    
    """
    seg, _, _= segment(data)
    weights = get_weights(seg, data)
    plt.figure(1, figsize=(10, 10))
    labels = list(weights.keys())
    fracs = [weights[key] for key in labels]
    sum_weight = sum(weight for weight in fracs)
    if sum_weight < 1:
        fracs.append(1 - sum_weight)
        labels.append('no segment')
    plt.pie(fracs, labels=labels, colors=plot_colors[:len(fracs)], autopct='%1.1f%%')
    plt.title('Temps passé dans chaque phase, en pourcentage de la durée du vol', bbox={'facecolor':'0.8', 'pad':5})
    plt.draw()


def plot_ports_seg(data):
    """
    For each phase, plot one pie chart for each side of the time spent on each port
    
    :param data: pd.DataFrame
    
    """
    _, ports, _ = segment(data)
    for each_segment, ports_on_segment in ports.items():
        ports[each_segment] = tuples_to_durations(ports_on_segment)
    f, axarr = plt.subplots(2, 7, figsize=(23, 7))
    f.suptitle('Utilisation des ports selon chaque phase', bbox={'facecolor':'0.8', 'pad':5})
    j = 0
    for each_segment in ports:
        labels = ports[each_segment].keys()  # pressure ports names
        labels_1 = [label for label in labels if label[-1]=='1'] + ['apu','no bleed'] # left pressure ports + apu
        labels_2 = [label for label in labels if label[-1]=='2'] + ['apu','no bleed'] # right pressure ports + apu
        fracs_1 = [ports[each_segment][key] for key in labels_1]
        fracs_2 = [ports[each_segment][key] for key in labels_2]
        colors = plot_colors[:len(labels)]
        axarr[0, j].pie(fracs_1, labels=labels_1, colors=colors, autopct='%1.1f%%')
        axarr[0, j].set_title('{} côté 1'.format(each_segment), bbox={'facecolor':'0.8', 'pad':5})
        axarr[1, j].pie(fracs_2, labels=labels_2, colors=colors, autopct='%1.1f%%')
        axarr[1, j].set_title('{} côté 2'.format(each_segment), bbox={'facecolor':'0.8', 'pad':5})
        j = (j+1)%7
    plt.show()


def plot_ports_sides(data):
    """
    Plot one pie chart for each side of the time spent on each port
    
    :param data: pd.DataFrame
    """
    _, _, ports_full_flight = segment(data)
    ports_durations = tuples_to_durations(ports_full_flight)
    _, axarr = plt.subplots(1, 2, figsize=(20, 10))
    labels = ports_durations.keys()  # pressure ports names
    for side in [1, 2]:
        labels_1 = [l for l in labels if l[-1] == str(side)] + ['apu', 'no bleed']
        fracs_1 = [ports_durations[key] for key in labels_1]
        axarr[side-1].pie(fracs_1, labels=labels_1, autopct='%1.1f%%',
                          colors=plot_colors[:len(labels)])
        axarr[side-1].set_title('côté '+str(side), bbox={'facecolor':'0.8', 'pad':5})
    plt.show()


def plot_ports(data):
    """
    Plot a pie chart of the percentage of time spent on each pressure port

    :param data
        pandas df
    """
    _, _, ports_full_flight = segment(data)
    flight_duration = data.Time.iloc[-1] - data.Time.iloc[0]
    ports_durations = tuples_to_durations(ports_full_flight)
    # Convert durations on each port into percentage of the flight duration
    for port in ports_durations.keys():
        ports_durations[port] /= flight_duration
    plt.figure(1, figsize=(10, 10))
    labels = ports_durations.keys()
    fracs = [ports_durations[key] for key in labels]
    colors = ['gold', 'yellowgreen', 'orange', 'lightskyblue', 'dodgerblue',
              'indianred', 'orchid'][:len(labels)]
    plt.pie(fracs, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title('Temps passé sur chaque port, en pourcentage de la durée du vol', bbox={'facecolor':'0.8', 'pad':5})
    plt.show()



if __name__ == "__main__":
    
    import glob
    
    results = {}
    for filename in glob.iglob('../../Desktop/Articles Liebherr/pie_data/*.txt'):
        print('\n' + filename)
        flight_data = txt_parser(filename)
        intervals, ports, ports_full_flight = segment(flight_data)
        print('landing : {}'.format(intervals['landing']))
        print('take_off : {}'.format(intervals['take_off']))
        print('otg : {}'.format(intervals['otg']))
        

    # Chemin relatif vers le fichier txt de données
    #data_path = '../../Desktop/Articles Liebherr/pie_data/E190-E2_20001_0088_29574_53580_request.txt'


    # data contient un DataFrame pandas
    #flight_data = txt_parser(data_path)

    #for key in seg.keys():
    #    print('Poids du segment {} : {}'.format(key,weights[key]))
    #    print(seg[key])
    #    print('#########')
    #print(ports['otg'])
    #weights_ports = get_weights_ports(ports,data)
    #print(weights_ports)

    #plot_seg(flight_data)
    #plot_ports_seg(flight_data)
    #plot_ports_sides(flight_data)
    #plot_ports(flight_data)
