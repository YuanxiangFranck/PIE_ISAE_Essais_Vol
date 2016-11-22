# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 19:07:28 2016

@author: Florent

DTW demo
"""

import numpy as np
import matplotlib.pyplot as plt

import sys,os
sys.path.append(os.path.abspath('..'))
from tools.dtw import DTW,DTW_dist,DTW_align_plot

S = np.array([0,0,1,1,1,1,1,0,0,0,0,1,1,1,0,0]);
T = np.array([0,0,2,2,2,2,2,0,0,0,0,0,2,2,2,0]) 

print('S = {}'.format(S))
print('T = {}'.format(T))
print('Squared Euclidean distance between S and T : ')
print(np.sum((S-T)**2))
print('DTW distance between S and T : ')
print(DTW_dist(S,T))
print('Alignment plot :')
DTW_align_plot(S,T)
plt.ylim([-0.5,3])
plt.show()
print('Dynamic Time Warping matrix :\n')
plt.imshow(DTW(S,T),interpolation='nearest')
