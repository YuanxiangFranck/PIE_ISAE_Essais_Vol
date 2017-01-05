# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 19:08:35 2017

@author: Florent

Flight analysis functions
"""

import sys,os
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser
from SignalData import SignalData
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize

def load_flight(path):
    print("Processing flight {}...".format(path))
    flight_data = txt_parser(path)
    # Cas particulier : la target '41psig'
    flight_data['41psig'] = 41
    return flight_data

def extract_sl_window(data, signals, sl_w, sl_s):
    # sliding window width
    sl_w = sl_w
    # sliding window stride
    sl_s = sl_s
    # number of samples
    m = (len(data)-sl_w)//sl_s+1 
    
    samples = [SignalData(data.loc[i*sl_s:i*sl_s+sl_w, signals]) for i in range(m)]
    return samples

def extract_sl_window_delta(data, signals1, signals2, sl_w, sl_s):
    assert(len(signals1) == len(signals2))
    
    def relative_delta(a,b):
        return (a-b)/b
    
    # sliding window width
    sl_w = sl_w
    # sliding window stride
    sl_s = sl_s
    # number of samples
    m = (len(data)-sl_w)//sl_s+1 
    # Compute delta between signal and target values
    dic = {}
    for i,name in enumerate(signals1):
        dat1 = data.loc[:, signals1]
        dat2 = data.loc[:, signals2]
        dic[signals1[i]+'_DELTA'] = relative_delta(dat1.iloc[:,i],dat2.iloc[:,i])
    delta = pd.DataFrame(dic)

    delta_samples = [SignalData(delta.loc[i*sl_s:i*sl_s+sl_w, :]) for i in range(m)]
    return delta_samples
    
def get_feature_matrix(samples, features, normalized=True, \
                       n_fft=10, n_dtc=10, threshold=0.1):
    
    n_features = len(features)
    if features.count('fft') > 0:
        n_features += 2*n_fft-1
    if features.count('dtc') > 0:
        n_features += 2*n_dtc-1
        
    n_signals = samples[0].data.shape[1]
    
    feature_matrix = np.zeros((len(samples),n_features*n_signals))
    
    for i,sigData in enumerate(samples):
        print(i)
        sigData.extractFeatures(features, n_fft=n_fft, \
                                n_dtc=n_dtc, threshold=threshold)
        # Store featurs as a row in feature matrix
        feature_matrix[i,:] = sigData.X.as_matrix().ravel()
        # Clear
        sigData.clearFeatures()
    
    # Normalize features
    if normalized:
        feature_matrix = normalize(feature_matrix,axis=0,norm='l1')
    return feature_matrix