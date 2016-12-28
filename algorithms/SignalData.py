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

from algorithms import signal_data_features
from dataProcessing.segmenter import segment as flight_segmenter

class SignalData:

    def __init__(self, signals, sl_window=None):
        """
        Stocke une liste de signaux donnés sous forme de Series pandas
        et les convertit en array numpy pour la suite du traitement.
        signals : list of pandas series
        """
        # Chargement des données et conversion en array numpy
        self.data  = signals.copy()
        self._raw_data = signals.copy()
        self.X = None
        self.sl_window = sl_window
        self.flight_segemnts = None

    def load(self, signals):
        self.__init__(signals)

    def reset_data(self):
        """
        Clear computed data and recover
        flight segments are kept
        """
        self.data = self._raw_data.copy()
        self.clearFeatures()

    def clearFeatures(self):
        self.X = None
        self.sl_window = None

    def clearAll(self):
        "Clear all attributes"
        self.clearFeatures()
        self.data = None
        self._raw_data = None
        self.flight_segemnts = None

    """
    Signal manipulation
    """
    def setSegmentation(self, w):
        """
        Segmentation du signal avec fenêtre de taille fixe.
        w : window size
        """
        self.sl_window = w

    def compute_flight_segmentation(self):
        "Compute flight segmentation and set current data to "
        self.flight_segemnts = flight_segmenter(self.data)
        # filtering is adding new columns
        self._raw_data = self.data.copy()

    def apply_flight_segmentation(self, segment):
        "Restrict data to a segmet of the flight segment"
        # Compute flight segmentation if it's not done
        if self.flight_segemnts is None:
            self.compute_flight_segmentation()
        # Check if the given segment is valid
        if segment not in self.flight_segemnts:
            raise Exception('Segement name not valide {} in {}'
                            .format(segment, self.flight_segemnts))
        # don't do anything if no segments
        if not len(self.flight_segemnts[segment]):
            print("Warning No segment found ")
        # Get all index in which the time is within a segment
        idx = np.zeros(self.data.index.size).astype(bool)
        for start, end in self.flight_segemnts[segment]:
            idx = idx | ((start < self.data.Time)&(self.data.Time < end))
        self.data = self.data[idx]
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
