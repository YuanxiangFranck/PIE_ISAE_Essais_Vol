# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:59:48 2016

@author: Florent

Main class for manipulating signal data and extracting features

data : whole signals or signal subsequences (only with 1 signal)
X    : features matrix
        
"""

import numpy as np

class SignalData:
    
    def __init__(self, signals):
        """
        Stocke une liste de signaux donnés sous forme de Series pandas
        et les convertit en array numpy pour la suite du traitement.
        signals : list of pandas series
        """
        # Chargement des données et conversion en array numpy
        self.data  = np.array([s.as_matrix() for s in signals])
        self.X = None
        
    def load(self, signals):
        self.__init__(signals)
    
    def setSlidingWindow(self, w):
        """
        Transformation du signal avec une sliding window.
        w : window size
        """
        if len(self.data) > 1:
            print('Slinding window transformation is only available for 1 signal!')
            return
        else:
            signal = self.data[0]
            m = len(signal)-w+1 # number of samples
            self.data = np.array([signal[i:i+w] for i in range(m)])
        
    def extractFeatures(self,feature_names):
        """
        Extrait les features de la liste donnée en argument
        et les ajoute à la matrice X
        feature_names : list of strings
        available features :
        mean, var, std, min, max, amplitude, covariance
        """
        for f in feature_names:
            if f == 'mean':
                tmp = self.get_mean()
            elif f == 'var':
                tmp = self.get_var()
            elif f == 'std':
                tmp = self.get_std()
            elif f == 'min':
                tmp = self.get_min()
            elif f == 'max':
                tmp = self.get_max()
            elif f == 'amplitude':
                tmp = self.get_amplitude()
            elif f == 'covariance':
                tmp = self.get_covariance()
            
            if self.X == None:
                self.X = tmp
            else:
                self.X = np.append(self.X,tmp,axis=1)
            
    """
    Méthodes de calcul de features
    """
    def get_mean(self):
        """
        Moyenne du signal
        """
        return np.mean(self.data,axis=1).reshape((-1,1))
    
    def get_var(self):
        """
        Variance du signal
        """
        return np.var(self.data,axis=1).reshape((-1,1))
        
    def get_std(self):
        """
        Ecart-type du signal
        """
        return np.std(self.data,axis=1).reshape((-1,1))
        
    def get_min(self):
        """
        Minimum du signal
        """
        return np.min(self.data,axis=1).reshape((-1,1))
        
    def get_max(self):
        """
        Maximum du signal
        """
        return np.max(self.data,axis=1).reshape((-1,1))
        
    def get_amplitude(self):
        """
        Amplitude du signal
        """
        return (np.max(self.data,axis=1) - np.min(self.data,axis=1)).reshape((-1,1))
    
    def get_covariance(self):
        """
        Matrice de covariance des signaux
        """
        return np.cov(self.data)
