# -*- coding: utf-8 -*-
"""
Created on Fri Jan 13 14:16:29 2017

@author: Florent

Script pour l'analyse des signaux de régulation d'un vol

Application d'un OCSVM (One-Class SVM) sur différentes 
features des segments temporels d'un vol
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

flight_name = 'E190-E2_20001_0083_29106_52495_request.txt'
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
if phase != 'all':
    flight_data.apply_flight_segmentation(phase)

#%%
"""
Extraction des signaux par sliding window
* n_samples : nombre de segments à découper par sliding window
* vous pouvez aussi fixer manuellement sl_w et sl_s
"""

n_samples = 100

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
    
samples = extract_sl_window_delta(flight_data.data, signal_names_regul, \
                            target_names_regul, sl_w, sl_s)

#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

from sklearn.preprocessing import scale

features = ['mean','std','percent_time_over_threshold']

feature_matrix = get_feature_matrix(samples, features, normalized=False)

feature_matrix = scale(feature_matrix)

#%%
"""
Visualisation des données par phase de vol
"""

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

reduced_data = PCA(n_components=2).fit_transform(feature_matrix)

plt.figure(figsize=(10,10))

color_dic = {'climb': "r", 'cruise': "b",
                               'landing': 'm',
                               'descent': 'g', 'hold': "c",
                               'otg': 'y', 'take_off': 'k'}
                               
if phase == 'all':
    flight_data.compute_flight_segmentation()
    
    phases = []
    for i in range(len(samples)):
        p = idx2phase(whole_flight.Time.iloc[0], whole_flight.Time.iloc[-1], \
                             flight_data.flight_segments, i, sl_w, sl_s)
        if p:
            phases.append(p[0])
        else:
            phases.append('missing')

    color_dic['missing'] = 'white'
    
    colors = [color_dic[phases[i]] for i in range(len(samples))]
        
    plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=colors, s=50)
    
else:
     plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=color_dic[phase], s=50)
     
for i in range(reduced_data.shape[0]):
    plt.text(reduced_data[i,0]+0.05,reduced_data[i,1],i)
    
#%%
"""
Analyse
OCSVM
"""

from sklearn import svm

ocsvm = svm.OneClassSVM(nu=0.5, kernel="rbf", gamma=0.1)
#ocsvm.fit(feature_matrix)
#predictions = ocsvm.predict(feature_matrix)
ocsvm.fit(reduced_data)
predictions = ocsvm.predict(reduced_data)

outliers = reduced_data[predictions == -1]

plt.figure(figsize=(10,10))

# Step size of the mesh. Decrease to increase the quality of the VQ.
h = 0.01     # point in the mesh [x_min, x_max]x[y_min, y_max].

# Plot the decision boundary. For that, we will assign a color to each
x_min, x_max = reduced_data[:, 0].min() - 0.01, reduced_data[:, 0].max() + 0.01
y_min, y_max = reduced_data[:, 1].min() - 0.01, reduced_data[:, 1].max() + 0.01
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))


Z = ocsvm.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.PuBu)
a = plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='darkred')
plt.contourf(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred')

s = 40
b1 = plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c='white', s=s)
c = plt.scatter(outliers[:, 0], outliers[:, 1], c='gold', s=s)

for i in range(reduced_data.shape[0]):
    plt.text(reduced_data[i,0]+0.05,reduced_data[i,1],i)

plt.title('- OCSVM Outlier detection -\n'\
      'Flight : {} / Phase : {}\n'\
      'Data : relative error between regulation and target signals\n'\
      'Features : {}\n'\
      'Time window : {} s'.format(flight_name,phase,features, sl_w))
    
plt.show()