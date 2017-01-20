# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 13:06:53 2017

@author: Florent

Détection de segments temporels anormaux dans un vol
"""

#%%
import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser
from SignalData import *
import pandas as pd
from sklearn.preprocessing import normalize

#%%
"""
Load flight and extract signals
"""
flight_name = 'E190-E2_20001_0085_29472_53398_request.txt'
path = '../../data/'

# selecting signals
signal_names_regul = \
['CPCS_CABIN_PRESS_AMSC1_CHA',
'CPCS_CABIN_PRESS_AMSC1_CHB',
'CPCS_CABIN_PRESS_AMSC2_CHA',
'CPCS_CABIN_PRESS_AMSC2_CHB',
'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC1_CHA',
'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC1_CHB',
'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC2_CHA',
'ACS_PACK_INLET_MASS_FLOW_CALC_AMSC2_CHB',
'ACS_MIX_TEMP_AMSC1_CHA',
'ACS_MIX_TEMP_AMSC1_CHB',
'ACS_MIX_TEMP_AMSC2_CHA',
'ACS_MIX_TEMP_AMSC2_CHB',
'ACS_ZONE1_DUCT_TEMP_AMSC1_CHA',
'ACS_ZONE1_DUCT_TEMP_AMSC1_CHB',
'ACS_ZONE1_DUCT_TEMP_AMSC2_CHA',
'ACS_ZONE1_DUCT_TEMP_AMSC2_CHB',
'ACS_ZONE2_DUCT_TEMP_AMSC1_CHA',
'ACS_ZONE2_DUCT_TEMP_AMSC1_CHB',
'ACS_ZONE2_DUCT_TEMP_AMSC2_CHA',
'ACS_ZONE2_DUCT_TEMP_AMSC2_CHB',
'ACS_ZONE1_TEMP_AMSC1_CHA',
'ACS_ZONE1_TEMP_AMSC1_CHB',
'ACS_ZONE1_TEMP_AMSC2_CHA',
'ACS_ZONE1_TEMP_AMSC2_CHB',
'ACS_ZONE2_TEMP_AMSC2_CHA',
'ACS_ZONE2_TEMP_AMSC2_CHB',
'BLEED_OUT_PRESS_AMSC1_CHA',
'BLEED_OUT_PRESS_AMSC1_CHB',
'BLEED_OUT_PRESS_AMSC2_CHA',
'BLEED_OUT_PRESS_AMSC2_CHB',
'BLEED_OUT_TEMP_AMSC1_CHA',
'BLEED_OUT_TEMP_AMSC1_CHB',
'BLEED_OUT_TEMP_AMSC2_CHA',
'BLEED_OUT_TEMP_AMSC2_CHB',
'APS_OUT_PRESS_AMSC1_CHA',
'APS_OUT_PRESS_AMSC1_CHB',
'APS_OUT_PRESS_AMSC2_CHA',
'APS_OUT_PRESS_AMSC2_CHB',
'APS_OUT_TEMP_AMSC1_CHA',
'APS_OUT_TEMP_AMSC1_CHB',
'APS_OUT_TEMP_AMSC2_CHA',
'APS_OUT_TEMP_AMSC2_CHB',
'WAI_CONTROLLING_PRESS_AMSC1_CHA',
'WAI_CONTROLLING_PRESS_AMSC1_CHB',
'WAI_CONTROLLING_PRESS_AMSC2_CHA',
'WAI_CONTROLLING_PRESS_AMSC2_CHB',
'WAI_OPP_CONTROLLING_PRESS_AMSC1_CHA',
'WAI_OPP_CONTROLLING_PRESS_AMSC1_CHB',
'WAI_OPP_CONTROLLING_PRESS_AMSC2_CHA',
'WAI_OPP_CONTROLLING_PRESS_AMSC2_CHB']

target_names_regul = \
['CPCS_PRESSURE_TARGET_AMSC1_CHA',
'CPCS_PRESSURE_TARGET_AMSC1_CHB',
'CPCS_PRESSURE_TARGET_AMSC2_CHA',
'CPCS_PRESSURE_TARGET_AMSC2_CHB',
'ACS_PACK_INLET_MASS_FLOW_TARGET_AMSC1_CHA',
'ACS_PACK_INLET_MASS_FLOW_TARGET_AMSC1_CHB',
'ACS_PACK_INLET_MASS_FLOW_TARGET_AMSC2_CHA',
'ACS_PACK_INLET_MASS_FLOW_TARGET_AMSC2_CHB',
'ACS_MIX_TEMP_TARGET_AMSC1_CHA',
'ACS_MIX_TEMP_TARGET_AMSC1_CHB',
'ACS_MIX_TEMP_TARGET_AMSC2_CHA',
'ACS_MIX_TEMP_TARGET_AMSC2_CHB',
'ACS_ZONE1_DUCT_TEMP_TARGET_AMSC1_CHA',
'ACS_ZONE1_DUCT_TEMP_TARGET_AMSC1_CHB',
'ACS_ZONE1_DUCT_TEMP_TARGET_AMSC2_CHA',
'ACS_ZONE1_DUCT_TEMP_TARGET_AMSC2_CHB',
'ACS_ZONE2_DUCT_TEMP_TARGET_AMSC1_CHA',
'ACS_ZONE2_DUCT_TEMP_TARGET_AMSC1_CHB',
'ACS_ZONE2_DUCT_TEMP_TARGET_AMSC2_CHA',
'ACS_ZONE2_DUCT_TEMP_TARGET_AMSC2_CHB',
'ACS_CKPT_TEMP_TARGET_AMSC1_CHA',
'ACS_CKPT_TEMP_TARGET_AMSC1_CHB',
'ACS_FWD_CAB_TEMP_TARGET_AMSC2_CHA',
'ACS_FWD_CAB_TEMP_TARGET_AMSC2_CHB',
'ACS_AFT_CAB_TEMP_TARGET_AMSC2_CHA',
'ACS_AFT_CAB_TEMP_TARGET_AMSC2_CHB',
'BLEED_OUT_PRESS_TARGET_AMSC1_CHA',
'BLEED_OUT_PRESS_TARGET_AMSC1_CHB',
'BLEED_OUT_PRESS_TARGET_AMSC2_CHA',
'BLEED_OUT_PRESS_TARGET_AMSC2_CHB',
'BLEED_OUT_TEMP_TARGET_AMSC1_CHA',
'BLEED_OUT_TEMP_TARGET_AMSC1_CHB',
'BLEED_OUT_TEMP_TARGET_AMSC2_CHA',
'BLEED_OUT_TEMP_TARGET_AMSC2_CHB',
'41psig',
'41psig',
'41psig',
'41psig',
'APS_OUT_TEMP_TARGET_AMSC1_CHA',
'APS_OUT_TEMP_TARGET_AMSC1_CHB',
'APS_OUT_TEMP_TARGET_AMSC2_CHA',
'APS_OUT_TEMP_TARGET_AMSC2_CHB',
'WAI_OUT_PRESS_TARGET_AMSC1_CHA',
'WAI_OUT_PRESS_TARGET_AMSC1_CHB',
'WAI_OUT_PRESS_TARGET_AMSC2_CHA',
'WAI_OUT_PRESS_TARGET_AMSC2_CHB',
'WAI_OUT_PRESS_TARGET_AMSC1_CHA',
'WAI_OUT_PRESS_TARGET_AMSC1_CHB',
'WAI_OUT_PRESS_TARGET_AMSC2_CHA',
'WAI_OUT_PRESS_TARGET_AMSC2_CHB']

signal_names_for_segmentation = \
['WOW_FBK_AMSC1_CHA',
'ADSP1 Pressure Altitude (feet)',
'ADSP1 Altitude Rate (ft/min)',
'ADSP1 Calibrated Airspeed (knots)']


print("Processing flight {}...".format(flight_name))
flight_data = txt_parser(path+flight_name)

#%%
"""
Extract and segment signals
"""

signal_names = signal_names_regul
target_names = target_names_regul

# sliding window width
sl_w = 60
# sliding window stride
sl_s = 30
# number of samples
m = (len(flight_data)-sl_w)//sl_s+1 

# Cas particulier : la target '41psig'
flight_data['41psig'] = 41

def relative_delta(a,b):
    return (a-b)/b

# Compute delta between signal and target values
dic = {}
for i,name in enumerate(signal_names):
    dat = flight_data.loc[:, signal_names]
    dat_target = flight_data.loc[:, target_names]
    dic[signal_names[i]+'_DELTA'] = relative_delta(dat.iloc[:,i],dat_target.iloc[:,i])
deltas = pd.DataFrame(dic)

# Extract deltas with sliding window
samples_deltas = [SignalData(deltas.loc[i*sl_s:i*sl_s+sl_w, :]) for i in range(m)]


#%%
"""
Extract features
"""

#features = ['mean','std','min','max']
features = ['time_over_threshold','mean_crossings']
threshold = 0.1
f_length = len(features)
#f_length = len(features)-1+2*n_fft

# Matrix containing each subsequence's features in a row
feature_matrix = np.zeros((m,f_length*len(signal_names)))
#feature_matrix = np.zeros((m,f_length))

for i,sigData in enumerate(samples_deltas):
    print(i)
    sigData.extractFeatures(features,threshold=threshold)
    # Store featurs as a row in feature matrix
    feature_matrix[i,:] = sigData.X.as_matrix().ravel()
    # Clear
    sigData.clearFeatures()

# Normalize features
feature_matrix = normalize(feature_matrix,axis=0,norm='l1')

#%%
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

reduced_data = PCA(n_components=2).fit_transform(feature_matrix)

x,y = reduced_data[:,0],reduced_data[:,1]
plt.scatter(x,y)
for i in range(m):
    plt.text(x[i]+0.01,y[i],i)
plt.title('PCA - features : {})'.format(features))

#%%
"""
Clustering
"""
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

n_clusters = 3

pca = PCA(n_components=2).fit(feature_matrix)
reduced_data = pca.transform(feature_matrix)
kmeans = KMeans(n_clusters=n_clusters).fit(reduced_data)

# Step size of the mesh. Decrease to increase the quality of the VQ.
h = 0.001     # point in the mesh [x_min, x_max]x[y_min, y_max].

# Plot the decision boundary. For that, we will assign a color to each
x_min, x_max = reduced_data[:, 0].min() - 0.01, reduced_data[:, 0].max() + 0.01
y_min, y_max = reduced_data[:, 1].min() - 0.01, reduced_data[:, 1].max() + 0.01
xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# Obtain labels for each point in mesh. Use last trained model.
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

# Put the result into a color plot
Z = Z.reshape(xx.shape)
plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

x,y = reduced_data[:,0],reduced_data[:,1]
plt.scatter(x,y)
for i in range(m):
    plt.text(x[i]+0.005,y[i],i)
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='o', linewidths=1,
            color='r')
plt.title('K-means clustering on signal-target rel. delta of flight subsequences (PCA-reduced data)\n \
sliding window : 60/30 \n \
flight : {} \n \
signals : regul / features : {}'.format(flight_name,features))
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.show()
