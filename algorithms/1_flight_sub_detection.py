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


#%%
"""
Load flight and extract signals
"""
flight_name = 'E190-E2_20001_0085_29472_53398_request.txt'
path = '../../data/'

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

signal_names_for_segmentation = \
['WOW_FBK_AMSC1_CHA',
'ADSP1 Pressure Altitude (feet)',
'ADSP1 Altitude Rate (ft/min)',
'ADSP1 Calibrated Airspeed (knots)',
'Time']


print("Processing flight {}...".format(flight_name))
flight_data = txt_parser(path+flight_name)

#%%
"""
Extract and segment signals
"""

# sliding window width
sl_w = 60
# sliding window stride
sl_s = 60
# number of samples
m = (len(flight_data)-sl_w)//sl_s+1 

samples = [SignalData(flight_data.loc[i*sl_s:i*sl_s+sl_w, signal_names]) for i in range(m)]

#%%
"""
Extract features
"""

features = ['mean','std','min','max']
#features = ['mean','std','min','max','fft']
n_fft = 10
f_length = len(features)
#f_length = len(features)-1+2*n_fft

# Matrix containing each subsequence's features in a row
feature_matrix = np.zeros((m,f_length*len(signal_names)))

for i,sigData in enumerate(samples):
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
for i in range(m):
    plt.text(x[i]+0.01,y[i],i)
plt.title('PCA - features : {})'.format(features))
