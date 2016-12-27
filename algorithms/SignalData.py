# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:59:48 2016

@author: Florent

Main class for manipulating signal data and extracting features

data : whole signals or signal subsequences (only with 1 signal)
X    : features matrix

"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
import signal_data_features

class SignalData:

    def __init__(self, signals, sl_window=None):
        """
        Stocke une liste de signaux donnés sous forme de Series pandas
        et les convertit en array numpy pour la suite du traitement.
        signals : list of pandas series
        """
        # Chargement des données et conversion en array numpy
        self.data  = signals.copy()
        self.X = None
        self.sl_window = sl_window

    def load(self, signals):
        self.__init__(signals)

    def clearFeatures(self):
        self.X = None

    def clearAll(self):
        self.data = None
        self.X = None
        self.sl_window = None

    """
    Signal manipulation
    """
    def setSegmentation(self, w):
        """
        Segmentation du signal avec fenêtre de taille fixe.
        w : window size
        """
        self.sl_window = w

    """
    Feature extraction
    """
    def useWholeTimeseries(self):
        """
        Utilisation des valeurs brutes des signaux à chaque pas de temps
        en tant que features.
        Attention : si le signal est long, cela génère trop de features
        pour certains algorithmes !
        """
        self.X = self.data.copy()

    def extractFeatures(self, feature_names, n_fft=10, n_dtc=10):
        """
        Extrait les features de la liste donnée en argument
        et les ajoute à la matrice X
        feature_names : list of strings
        n_fft (optional) : number of Fourier coefficients

        available features :
        mean, var, std, min, max, amplitude, covariance,
        binary_transitions, fft, dtc (discrete cosine transform)
        """
        agg = {}
        # Get function names
        for f in feature_names:
            if f == 'fft':
                fun = lambda x: signal_data_features.get_fft(x, n_fft)
            elif f == 'dtc':
                fun = lambda x: signal_data_features.get_dct(x, n_dtc)
            else:
                fun = getattr(signal_data_features, "get_"+f)
            agg[f] = fun
        # If raw data (no sliding window)
        if self.sl_window is None:
            computed_features = {f: self.data.apply(fun, axis=0)
                                 for f, fun in agg.items()}
            self.X = pd.DataFrame(computed_features).transpose()
        else:
            computed_features = []
            # return a multi indexed dataframe
            multi_indexed_res = self.data.rolling(self.sl_window).agg(agg)
            for f in feature_names:
                tmp = multi_indexed_res[f]
                tmp.index = [f]*len(tmp.index)
                computed_features.append(tmp)
            self.X = pd.concat(computed_features)


    def normalizeFeatures(self):
        self.X = normalize(self.X,axis=0,norm='l1')
