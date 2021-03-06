# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 19:08:35 2017

@author: Florent

Flight analysis functions
"""

import sys,os
import logging
sys.path.append(os.path.abspath('..'))
from dataProcessing.parser import txt_parser
from algorithms.SignalData import SignalData
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize

def load_flight(path):
    logging.info("Processing flight {}...".format(path))
    flight_data = txt_parser(path)
    return flight_data

def extract_sl_window(data, signals, sl_w, sl_s, n_samples):
    return [SignalData(data.loc[i*sl_s:i*sl_s+sl_w, signals])
            for i in range(n_samples)]

def extract_sl_window_delta(data, signals1, signals2, sl_w, sl_s,
                            n_samples, delta_type):
    assert(len(signals1) == len(signals2))

    def relative_delta(a_series,b_series):
        res = []
        for a,b in zip(a_series,b_series):
            if a == b == 0.: res.append(0)
            else: res.append( 2.*(a-b)/(np.abs(a)+np.abs(b)) )
        return res

    def absolute_delta(a_series,b_series):
        res = []
        for a,b in zip(a_series,b_series):
            res.append(np.abs(a-b))
        return res

    # Compute delta between signal and target values
    dic = {}
    for i, name in enumerate(signals1):
        dat1 = data.loc[:, signals1]
        dat2 = data.loc[:, signals2]
        if delta_type[i] == 'rel':
            dic[name+'_DELTA'] = relative_delta(dat1.iloc[:, i], dat2.iloc[:, i])
        else:
            dic[name+'_DELTA'] = absolute_delta(dat1.iloc[:, i], dat2.iloc[:, i])
    delta = pd.DataFrame(dic)

    delta_samples = [SignalData(delta.iloc[i*sl_s:i*sl_s+sl_w, :]) for i in range(n_samples)]
    return delta_samples

def get_feature_matrix(samples, features, normalized=False,
                       n_fft=10, n_dtc=10, threshold=0.1):
    """
    TODO DOCSTRING
    """
    n_features = len(features)
    if features.count('fft') > 0:
        n_features += 2*n_fft-1
    if features.count('dtc') > 0:
        n_features += 2*n_dtc-1

    n_signals = samples[0].data.shape[1]

    feature_matrix = np.zeros((len(samples),n_features*n_signals))

    for i, sigData in enumerate(samples):
        sigData.extractFeatures(features, n_fft=n_fft,
                                n_dtc=n_dtc, threshold=threshold)
        # Store featurs as a row in feature matrix
        feature_matrix[i, :] = sigData.X.as_matrix().ravel()
        # Clear
        sigData.clearFeatures()

    # Normalize features
    if normalized:
        feature_matrix = normalize(feature_matrix, axis=0, norm='l1')
    return feature_matrix

def idx2date(dates, idx, sl_w, sl_s):
    """
    Get real time segments corresponding to the index of a sample
    in a sliding window decomposition with parameters sl_w, sl_s

    Warning : this function takes into consideration the case when the time
    window overlaps on two occurrences of the same flight phase. However, it
    won't work if an occurence of the flight phase is shorter than the time
    window sl_w itself !
    """
    i_start,i_stop = 0,0
    remaining = 0
    elapsed = 0
    # find start index
    for i in range(len(dates)):
        if dates[i][0] + idx*sl_s - elapsed <= dates[i][1]:
            i_start = i
            remaining = dates[i_start][0] + idx*sl_s + sl_w \
                        - elapsed - dates[i_start][1]
            break
        elapsed += dates[i][1] - dates[i][0]
    # if overlap, set stop index to the next occurence
    if remaining > 0:
        i_stop = i_start+1
        return (dates[i_start][0] + idx * sl_s - elapsed, dates[i_start][1],\
                dates[i_stop][0], dates[i_stop][0] + remaining)
    else:
        return (dates[i_start][0] + idx * sl_s - elapsed, \
                dates[i_start][0] + idx * sl_s + sl_w - elapsed)

def idx2phase(start, stop, flight_segments, idx, sl_w, sl_s):
    for phase in flight_segments.items():
        phase_name, phase_dates = phase
        for i,dates in enumerate(phase_dates):
            if dates[0] <= idx2date([(start,stop)], idx, sl_w, sl_s)[0] <= dates[1]:
                return phase_name,i

def idx2port(start, stop, ports, idx, sl_w, sl_s):
    sides = (('apu', 'hp1', 'ip1', 'no bleed'),
             ('apu', 'hp2', 'ip2', 'no bleed'))
    res = [None, None]
    for k,side in enumerate(sides):
        for port in ports.items():
            port_name, port_dates = port
            if port_name in side:
                for i,dates in enumerate(port_dates):
                    if dates[0] <= idx2date([(start,stop)], idx, sl_w, sl_s)[0] <= dates[1]:
                        res[k] = port_name,i
    return res
