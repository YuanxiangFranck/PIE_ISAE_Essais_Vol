# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 16:02:12 2016

@author: Florent Forest
"""

"""
Dynamic Time Warping
"""

import numpy as np

def DTW_dist(S,T):
    "Compute DTW distance between two timeseries"
    return DTW(S,T)[-1,-1] # return last element of DTW matrix

def DTW_align(S,T):
    "Compute DTW alignment of two timeseries" 
    n = len(S)
    m = len(T)
    dtw = DTW(S,T)
    i,j = 0,0
    align = [[i,j]]
    while(i < n-1 or j < m-1):
        # if we reached the end of S
        if i == n-1:
            # go forward in T
            j = j+1
        # if we reached the end of T
        elif j == m-1:
            # go forward in S
            i = i+1
        else:
            # choose the shorter path in matrix
            idx = np.argmin([dtw[i+1,j],dtw[i,j+1],dtw[i+1,j+1]])
            if idx == 0:
                # go forward in S 
                i = i+1
            elif idx == 1:
                # go forward in T
                j = min(j+1,m-1)
            else:
                # go forward in both S and T
                i = i+1
                j = j+1
        align.append([i,j])
    return(np.array(align))
            

def DTW(S,T):
    "Compute DTW matrix of two timeseries"
    n = len(S)
    m = len(T)
    dtw = np.zeros((n,m))
    
    for i in range(1,n):
        cost = np.abs(S[i]-T[0])
        dtw[i,0] = dtw[i-1,0]  + cost
    for j in range(1,m):
        cost = np.abs(S[0]-T[j])
        dtw[0,j] = dtw[0,j-1]  + cost
    
    for i in range(1,n):
        for j in range(1,m):
            cost = np.abs(S[i]-T[j])
            dtw[i,j] = cost + min(dtw[i-1,j],   # insertion
                                  dtw[i,j-1],   # deletion
                                  dtw[i-1,j-1]) # match
    return dtw

def FastDTW(S,T,w):
    "Compute DTW matrix of two timeseries with FastDTW algorithm"
    raise NotImplemented
    