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

flight_name = 'E190-E2_20001_0092_29998_54590_request.txt'
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

"""
Chargement des valeurs d'écarts tolérées pour chaque signal de régulation,
ainsi que son type (relatif/absolu)
"""
target_precisions = pd.read_csv('target_precisions.csv', header=0, sep='\t')

thresholds = target_precisions['Precision'].as_matrix()
delta_type = target_precisions['Type'].as_matrix()
    
samples = extract_sl_window_delta(flight_data.data, signal_names_regul, \
                                  target_names_regul, sl_w, sl_s, delta_type)

#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

features = ['percent_time_over_threshold']

feature_matrix = get_feature_matrix(samples, features, normalized=False, \
                                    threshold=thresholds)

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

# Affichage de la phase de vol
color_dic = {'climb': 'r', 'cruise': 'b',
             'landing': 'm',
             'descent': 'g', 'hold': 'c',
             'otg': 'y', 'take_off': 'k'}

if phase == 'all':
    phases = []
    for i in range(n_samples):
        p = idx2phase(whole_flight.Time.iloc[0], whole_flight.Time.iloc[-1], \
                             flight_data.flight_segments, i, sl_w, sl_s)
        if p:
            phases.append(p[0])
        else:
            phases.append('missing')

    color_dic['missing'] = 'white'

    phase_cmap = ListedColormap([color_dic[phases[i]] \
                                 for i in range(n_samples)])

fig = plt.figure(figsize=(10*n_samples//20,10))
gs = gridspec.GridSpec(2, 1, height_ratios=[1, 50])

ax0 = plt.subplot(gs[0])
ax0.imshow(np.arange(n_samples).reshape(1,-1), cmap=phase_cmap, \
             interpolation='nearest')
ax0.set_axis_off()
ax0.grid(False)
        
ax1 = plt.subplot(gs[1])                              
sns.heatmap(feature_matrix.T, xticklabels = time_labels, \
            yticklabels=sorted(signal_names_regul), annot=False, ax=ax1)

box1 = ax1.get_position()
box0 = ax0.get_position()
ax0.set_position([box1.x0, box0.y1-0.095, box1.x1-box1.x0,0.04])

def create_proxy(c):
    line = Line2D([0],[0],color=c,marker='s',linestyle='None')
    return line
    
proxies = [create_proxy(color) for color in color_dic.values()]
fig.legend(proxies, color_dic.keys(), numpoints=1, markerscale=2, \
           loc=(0.89,0.695), ncol=1)

ax0.set_title('- Percent time off-regulation -\n'\
          'Flight : {} / Phase : {}\n'
          'Data : regulation and target signals\n'\
          'Time window : {} s'.format(flight_name,phase,sl_w))

#plt.savefig('test.pdf', bbox_inches='tight')

plt.show()