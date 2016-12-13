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
Load all flights and extract features
"""
flight_names = os.listdir('../../data')
path = '../../data/'

# Matrix containing each flight's features in a row
features = ['mean','min','max']
feature_matrix = np.zeros((len(flight_names),len(features)*1000))

for i,flight in enumerate(flight_names):
    print("Processing flight {}...".format(flight))
    flight_data = txt_parser(path+flight)
    # Extract all signals
    signal_names = flight_data.columns.values
    # using 1000 signals for the test
    signals = [flight_data[sig[0]].iloc[:,0] for sig in signal_names[:1000]]

    # Extract features for each flight
    sigData = SignalData(signals)
    sigData.extractFeatures(features)
    # Normalize features
    sigData.normalizeFeatures()
    # Store featurs as a row in feature matrix
    feature_matrix[i,:] = sigData.X.ravel()
    

#%%
from sklearn.decomposition import PCA

reduced_data = PCA(n_components=2).fit_transform(feature_matrix)

