# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 18:24:10 2017

@author: Florent

Script pour l'analyse des signaux binaires d'un vol

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
Import des noms de signaux et noms de vols
* signal_names_regul : signaux de régulation
* target_names_regul : cibles des signaux de régulation
* signal_names_for_segmentation : signaux utilisés pour la segmentation
* signal_names_bin : signaux binaires
"""
from signal_names import signal_names_bin
from flight_names import flight_names

#%%
"""
Sélection et chargement du vol
* modifier le path relatif si besoin
"""

flight_name = flight_names[1]
path = '../../data/'

whole_flight = load_flight(path+flight_name)

flight_data = SignalData(whole_flight)

# Suppression des signaux binaires qui ne se trouvent pas
# dans les données de vol
signal_names_bin_copy = signal_names_bin.copy()
cc = 0
for s in signal_names_bin_copy:
    if not s in whole_flight.columns.values:
        cc += 1
        signal_names_bin.remove(s)
print('Removed {}/{} signals not present in flight data.'.format(cc,len(signal_names_bin_copy)))
del signal_names_bin_copy

#%%
"""
Segmentation et sélection de la phase de vol
* all : garder toutes les phases
* climb/cruise/descent/hold/landing/otg/take_off
"""

phase = 'all'

flight_data.reset_data()
flight_data.compute_flight_segmentation()

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
    
samples = extract_sl_window(flight_data.data, signal_names_bin, \
                            sl_w, sl_s)

#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

features = ['nb_transitions']

feature_matrix = get_feature_matrix(samples, features, normalized=False)

#%%
"""
Preprocessing
élimination des signaux avec aucun changement d'état
"""
non_zero_signal_idx = []

for i in range(feature_matrix.shape[1]):
    if (feature_matrix[:,i] != 0).any():
        non_zero_signal_idx.append(i)

feature_matrix = feature_matrix[:,non_zero_signal_idx]

non_zero_signal_names = []
for idx in non_zero_signal_idx:
    non_zero_signal_names.append(signal_names_bin[idx])

#%%
# Trier les signaux par nb de changements
ordre = np.argsort(-np.sum(feature_matrix, axis=0))

feature_matrix = feature_matrix[:,ordre]
for i in range(len(non_zero_signal_names)):
    non_zero_signal_names[i] = non_zero_signal_names[ordre[i]]

#feature_matrix = np.clip(feature_matrix, 0, 40)

#%%
"""
Analyse
Heatmap
"""

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import gridspec
from matplotlib.lines import Line2D
import seaborn as sns


if phase != 'all':
    time_labels = [idx2date(flight_data.flight_segments[phase],\
                           idx,sl_w,sl_s) for idx in range(n_samples)]
else:
    origin = flight_data.data.Time.iloc[0]
    end = flight_data.data.Time.iloc[-1]
    time_labels = [idx2date([(origin,end)],\
                           idx,sl_w,sl_s) for idx in range(n_samples)]
                            
################################
# Affichage de la phase de vol #
################################

phase_color_dic = {'climb': 'r', 'cruise': 'b', 'landing': 'm', \
                    'descent': 'g', 'hold': 'c', 'otg': 'y', \
                    'take_off': 'k', 'missing': 'white'}

if phase == 'all':
    phases = []
    for i in range(n_samples):
        p = idx2phase(whole_flight.Time.iloc[0], whole_flight.Time.iloc[-1], \
                             flight_data.flight_segments, i, sl_w, sl_s)
        if p:
            phases.append(p[0])
        else:
            phases.append('missing')

    phase_cmap = ListedColormap([phase_color_dic[phases[i]] \
                                 for i in range(n_samples)])
else:
    phase_cmap = ListedColormap([phase_color_dic[phase] \
                                 for i in range(n_samples)])

#######################
# Affichage des ports #
#######################

port_color_dic = {'apu': 'g', 'ip1': 'c', 'ip2': 'b', 'hp1': 'orange', \
             'hp2': 'r', 'no bleed': 'k', 'missing': 'white'}

if phase == 'all':
    ports = []
    for i in range(n_samples):
        p = idx2phase(whole_flight.Time.iloc[0], whole_flight.Time.iloc[-1], \
                             flight_data.ports, i, sl_w, sl_s)
        if p:
            ports.append(p[0])
        else:
            ports.append('missing')
    
    port_cmap = ListedColormap([port_color_dic[ports[i]] \
                             for i in range(n_samples)])
else:
    # TO DO
    pass

def create_proxy(c):
        line = Line2D([0],[0],color=c,marker='s',linestyle='None')
        return line
    
phase_proxies = [create_proxy(color) for color in phase_color_dic.values()]
port_proxies = [create_proxy(color) for color in port_color_dic.values()]
    
##################################
# Boucle de création des figures #
##################################
# Nombre de signaux par heatmap
n_sig = 50
# Nombre de heatmaps à générer
n_heatmaps = len(non_zero_signal_names)//n_sig

def create_heatmap(k, start, stop):

    #########################
    # Création de la figure #
    #########################
    
    fig = plt.figure(figsize=(10*n_samples//20,10))
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 50])
    
    # Phases
    ax0 = plt.subplot(gs[0])
    ax0.imshow(np.arange(n_samples).reshape(1,-1), cmap=phase_cmap, \
                 interpolation='nearest')
    ax0.set_axis_off()
    ax0.grid(False)
    
    # Ports
    ax1 = plt.subplot(gs[1])
    ax1.imshow(np.arange(n_samples).reshape(1,-1), cmap=port_cmap, \
                 interpolation='nearest')
    ax1.set_axis_off()
    ax1.grid(False)
    
    ax2 = plt.subplot(gs[2])
    sns.heatmap(feature_matrix.T[start:stop], \
                xticklabels = time_labels, \
                yticklabels=non_zero_signal_names[start:stop], \
                annot=False, ax=ax2, robust=True)
    
    box0 = ax0.get_position()
    box1 = ax1.get_position()
    box2 = ax2.get_position()
    
    ax0.set_position([box2.x0, box0.y1-0.095, box2.x1-box2.x0, 0.04])
    ax1.set_position([box2.x0, box0.y1-0.125, box2.x1-box2.x0, 0.04])
    
    fig.legend(phase_proxies, phase_color_dic.keys(), numpoints=1, markerscale=2, \
               loc=(0.89,0.695), ncol=1)
    
    fig.legend(port_proxies, port_color_dic.keys(), numpoints=1, markerscale=2, \
               loc=(0.89,0.495), ncol=1)
                                                 
    ax0.set_title('- Binary transitions -\n'\
              'Flight : {} / Phase : {}\n'
              'Data : binary signals\n'\
              'Time window : {} s'.format(flight_name,phase, sl_w))
    
    plt.savefig('../../Resultats/heatmap/{}/hm_bin_transitions_all-{}.pdf'\
                .format(flight_name,k), bbox_inches='tight')
    
    plt.clf()

for k in range(n_heatmaps):
    create_heatmap(k, k*n_sig, (k+1)*n_sig)
# Création de la dernière figure
create_heatmap(k+1, (k+1)*n_sig, len(non_zero_signal_names))
