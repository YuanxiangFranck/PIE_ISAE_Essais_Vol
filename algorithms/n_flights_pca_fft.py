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
features = ['fft']
n_fft = 20
f_length = 2*n_fft
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
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

reduced_data = PCA(n_components=2).fit_transform(feature_matrix)

x,y = reduced_data[:,0],reduced_data[:,1]
plt.scatter(x,y)
for i in range(len(flight_names)):
    plt.text(x[i]+0.01,y[i],flight_names[i][14:30])
plt.title('PCA - features : FFT ({} coeffs)'.format(n_fft))
