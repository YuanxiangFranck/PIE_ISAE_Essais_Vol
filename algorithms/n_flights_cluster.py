# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 13:59:46 2016

@author: Florent

Détection de vols anormaux
"""

#%%
import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser
from SignalData import *


#%%
"""
Load all flights and extract signals
"""
flight_names = os.listdir('../../data')
path = '../../data/'
sigData_l = []
# selecting signals
# 1. regulation (continuous)
signal_names = \
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


for flight in flight_names:
    print("Processing flight {}...".format(flight))
    flight_data = txt_parser(path+flight)
    # Extract signals
    #signal_names = flight_data.columns.values
    
    signals = [flight_data[sig] for sig in signal_names]

    # Extract features for each flight
    sigData_l.append(SignalData(signals))
    
#%%
"""
Extract features
"""

# Matrix containing each flight's features in a row
features = ['mean','std','min','max']
#features = ['mean','std','min','max','fft']
n_fft = 10
f_length = len(features)
#f_length = len(features)-1+2*n_fft

feature_matrix = np.zeros((len(flight_names),f_length*len(signal_names)))

for i,sigData in enumerate(sigData_l):
    print(i)
    sigData.extractFeatures(features,n_fft)
    # Normalize features
    sigData.normalizeFeatures()
    # Store featurs as a row in feature matrix
    feature_matrix[i,:] = sigData.X.ravel()
    # Clear
    sigData.clearFeatures()

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
for i in range(len(flight_names)):
    plt.text(x[i]+0.005,y[i],flight_names[i][14:30])
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='o', linewidths=1,
            color='r')
plt.title('K-means clustering on flights (PCA-reduced data)\n \
signals : regul / features : {}'.format(features))
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.show()