# -*- coding: utf-8 -*-
"""
Created on Sat Nov 12 18:59:48 2016

@author: Florent


"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize

from algorithms import signal_data_features
from dataProcessing.segmenter import segment as flight_segmenter

class SignalData:
    """

    Main class for manipulating signal data and extracting features

    Usefull to do:

    * flight segmentation
    * features extraction
    * data noramalization

    Attributes:

    * data : whole signals or signal subsequences (only with 1 signal)
    * X    : features matrix

    """

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
        self.flight_segments = None
        self.ports = None

    def load(self, signals):
        "Reload a signal see init"
        self.__init__(signals)

    def reset_data(self):
        """
        Clear computed data and recover
        flight segments are kept
        """
        self.data = self._raw_data.copy()
        self.clearFeatures()

    def clearFeatures(self):
        """
        Clear computed features
        keep:

        * data / raw data
        * flight segments
        * window size

        """
        self.X = None

    def clearAll(self):
        "Clear all attributes"
        self.clearFeatures()
        self.data = None
        self._raw_data = None
        self.flight_segments = None
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

    def compute_flight_segmentation(self):
        "Compute flight segments and ports, and set attributes."
        self.flight_segments, _, _ = flight_segmenter(self.data)

    def set_flight_segments(self, phases):
        "Set flight_segments attribute"
        self.flight_segments = phases

    def apply_flight_segmentation(self, segment):
        "Restrict data to a segment of the flight segment"
        # Compute flight segmentation if it's not done
        if self.flight_segments is None:
            self.compute_flight_segmentation()
        # Check if the given segment is valid
        if segment not in self.flight_segments:
            raise Exception('Segment name not valid {} in {}'
                            .format(segment, self.flight_segments))
        # don't do anything if no segments
        if not len(self.flight_segments[segment]):
            print("Warning No segment found ")
        # Get all indices in which the time is within a segment
        idx = np.zeros(self.data.index.size).astype(bool)
        for start, end in self.flight_segments[segment]:
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

    def extractFeatures(self, feature_names, n_fft=10, n_dtc=10, threshold=1.0, ravel_features=True):
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
            elif f == 'time_over_threshold':
                fun = lambda x: signal_data_features.get_time_over_threshold(x, threshold)
            elif f == 'percent_time_over_threshold':
                fun = lambda x: signal_data_features.get_percent_time_over_threshold(x, threshold)
            elif f == 'threshold_crossings':
                fun = lambda x: signal_data_features.get_threshold_crossings(x, threshold)
            else:
                fun = getattr(signal_data_features, "get_"+f)
            agg[f] = fun
        # If raw data (no sliding window)
        if self.sl_window is None:
            new_features_name = []
            computed_features = {}
            for f, fun in agg.items():
                data = fun(self.data)
                if f == 'fft':
                    for i in range(data.shape[1]):
                        new_features_name.append(f + str(i))
                        computed_features[f + str(i)] = data[:, i]

                else:
                    new_features_name.append(f)
                    computed_features[f] = data
            self.X = pd.DataFrame(computed_features).loc[:, new_features_name]
        else:
            computed_features = []
            # return a multi indexed dataframe
            # [TODO] A TESTER !!!
            multi_indexed_res = self.data.rolling(window=self.sl_window, min_periods=1).agg(agg)
            if ravel_features:
                for f in feature_names:
                    tmp = multi_indexed_res[f]
                    tmp.index = [f]*len(tmp.index)
                    computed_features.append(tmp)
                self.X = pd.concat(computed_features).transpose()
            else:
                self.X = multi_indexed_res.transpose()


    def normalizeFeatures(self, keep_dataFrame=False):
        """
        Normalize the feature matrix

        :param [keep_dataFrame=False]: bool
            return data as a pandas dataframe to keep index and columns
        """
        data = normalize(self.X, axis=0, norm='l1')
        if keep_dataFrame:
            idx = self.X.index
            cols = self.X.columns
            self.X = pd.DataFrame(data=data, columns=cols, index=idx)
        else:
            self.X = data
