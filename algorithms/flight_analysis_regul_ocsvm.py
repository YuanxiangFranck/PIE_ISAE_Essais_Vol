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
* signal_names_endogene : signaux endogènes
"""
from signal_names import signal_names_regul, signal_names_endogene
from flight_names import flight_names

#%%
"""
Sélection et chargement du vol
* modifier le path relatif si besoin
"""

flight_name = flight_names[0]
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

"""
Choix des signaux à extraire

"""
selected_signals = signal_names_regul+signal_names_endogene
data_label = 'all regulation signals'

#samples = extract_sl_window_delta(flight_data.data, signal_names_regul, \
#                            target_names_regul, sl_w, sl_s)
samples = extract_sl_window(flight_data.data, selected_signals, sl_w, sl_s)

#%%
"""
Calcul des features
* les features sont stockées dans un array numpy
  de dimension (nb de segments * nb de features)
"""

from sklearn.preprocessing import scale

features = ['mean', 'std', 'amplitude']

feature_matrix = get_feature_matrix(samples, features, normalized=False)

feature_matrix = scale(feature_matrix)

#%%
"""
Visualisation par PCA des features par phase de vol
Association d'une couleur à chaque phase
"""

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

reduced_data = PCA(n_components=2).fit_transform(feature_matrix)

plt.figure(figsize=(10,10))

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

    colors = [phase_color_dic[phases[i]] for i in range(n_samples)]
    
    for col in phase_color_dic.items():
        p,c = col
        plt.scatter([reduced_data[i, 0] for i in range(n_samples) if colors[i] == c], \
                    [reduced_data[i, 1] for i in range(n_samples) if colors[i] == c], \
                    c=c, label=p, alpha=0.7, s=60)

    plt.legend(scatterpoints=1)

# une seule phase
else:
     plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=phase_color_dic[phase], \
                 label=phase, alpha=0.5, s=60)
     plt.legend(scatterpoints=1)
     
for i in range(reduced_data.shape[0]):
    plt.text(reduced_data[i,0]+0.2,reduced_data[i,1],i)

    #%%
"""
Visualisation par PCA des features par port débitant
Association d'une couleur à chaque port
"""

plt.figure(figsize=(10,10))

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

    colors = [port_color_dic[ports[i]] for i in range(n_samples)]
    
    for col in port_color_dic.items():
        p,c = col
        plt.scatter([reduced_data[i, 0] for i in range(n_samples) if colors[i] == c], \
                    [reduced_data[i, 1] for i in range(n_samples) if colors[i] == c], \
                    c=c, label=p, alpha=0.7, s=60)

    plt.legend(scatterpoints=1)

# une seule phase
else:
     #TO DO
     pass

for i in range(reduced_data.shape[0]):
    plt.text(reduced_data[i,0]+0.2,reduced_data[i,1],i)
#%%
"""
Analyse
OCSVM
"""

# OCSVM on reduced data

from sklearn import svm

nu = 0.3
gamma = 0.1
ocsvm = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)

ocsvm.fit(reduced_data)
predictions = ocsvm.predict(reduced_data)

outliers = reduced_data[predictions == -1]

plt.figure(figsize=(12,10))

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
      'nu = {} / gamma = {}\n'\
      'Flight : {} / Phase : {}\n'\
      'Data : {}\n'\
      'Features : {}\n'\
      'Time window : {} s'.format(gamma, nu, flight_name, phase, data_label, \
      features, sl_w))
    
plt.show()

#%%
# OCSVM on original high-dimensional data

ocsvm.fit(feature_matrix)
predictions = ocsvm.predict(feature_matrix)

anomalies = {}
anomalies['global'] = (predictions == -1)

#%%
"""
OCSVM par signal
"""

signal_prefix = list(set((s.split('_AMSC')[0] for s in selected_signals)))
signal_suffix = list('_AMSC{}_CH{}'.format(x,y) for x in [1,2] for y in ['A','B'])

for prefix in signal_prefix:
    ps_selected_signals = [prefix + suffix for suffix in signal_suffix]

    ps_samples = extract_sl_window(flight_data.data, ps_selected_signals, sl_w, sl_s)

    features = ['mean', 'std', 'amplitude']

    ps_feature_matrix = get_feature_matrix(ps_samples, features, normalized=False)

    ps_feature_matrix = scale(ps_feature_matrix)

    ocsvm.fit(ps_feature_matrix)
    ps_predictions = ocsvm.predict(ps_feature_matrix)

    anomalies[prefix] = (ps_predictions == -1)

#%%
"""
Génération d'une heatmap d'anomalies
"""

import matplotlib.pyplot as plt
import seaborn as sns

anomaly_matrix = np.zeros((len(signal_prefix)+1, n_samples))

anomaly_matrix[0,:] = anomalies['global']

for i,s in enumerate(signal_prefix):
    for j in range(n_samples):
        anomaly_matrix[i+1,j] = anomalies[s][j]


if phase != 'all':
    time_labels = [idx2date(flight_data.flight_segments[phase],\
                           idx,sl_w,sl_s) for idx in range(n_samples)]
else:
    origin = flight_data.data.Time.iloc[0]
    end = flight_data.data.Time.iloc[-1]
    time_labels = [idx2date([(origin,end)],\
                           idx,sl_w,sl_s) for idx in range(n_samples)]

fig = plt.figure(figsize=(10,30))

sns.heatmap(anomaly_matrix.T, yticklabels = time_labels, \
            xticklabels=['global'] + signal_prefix, annot=False, \
            cmap='Reds', cbar=False)

plt.savefig('../../Resultats/OCSVM/ocsvm_anomaly_heatmap.pdf', bbox_inches='tight')

#%%
"""
Génération d'un rapport d'anomalies
"""

report = {}
report['Time frame'] = time_labels
report['Phase'] = phases
report['Anomaly'] = anomalies['global']
report['Anomaly score'] = [sum(anomalies[s][i] for s in signal_prefix) \
                           for i in range(n_samples)]
report['Anomalous signals'] = \
[', '.join([s for s in signal_prefix if anomalies[s][i]]) \
           for i in range(n_samples)]

pd.DataFrame(report).to_csv('../../Resultats/OCSVM/anomaly_report.csv', \
        columns = ['Time frame', 'Phase', 'Anomaly', 'Anomaly score', \
        'Anomalous signals'], index_label = 'Time Id')
