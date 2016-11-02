# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 16:02:12 2016

@author: Florent Forest
"""

"""
Dynamic Time Warping distance measure
"""

import numpy as np

def DTWDist(S,T):
    "Compute DTW distance between two timeseries"
    n = len(S)
    m = len(T)
    dtw = np.zeros((n+1,m+1))
    
    for i in range(1,n+1):
        dtw[i,0] = np.inf
    for j in range(1,m+1):
        dtw[0,j] = np.inf
    
    for i in range(0,n):
        for j in range(0,m):
            #cost = d(s[i], t[j]) TO DO
            cost = abs(S[i]-T[j])
            dtw[i+1,j+1] = cost + min(dtw[i-1,j],   # insertion
                                      dtw[i,j-1],   # deletion
                                      dtw[i-1,j-1]) # match
    return dtw,dtw[n,m]