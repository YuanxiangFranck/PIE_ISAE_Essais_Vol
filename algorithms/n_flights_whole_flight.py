# -*- coding: utf-8 -*-
"""
Created on Wen March 01 

@author: Quentin

Visualization of n flights
"""
import json
import matplotlib.pyplot as plt
import pandas as pd
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment
from dataProcessing.segmenter_utils import get_weights
from sklearn.decomposition import PCA



def plot_pca(files_names,
             features=['climb','cruise','descent','hold','landing','otg','take_off','apu','hp1','hp2','ip1','ip2','no bleed'],
             config_path="data_info/config.json"):
    """
    Plot several flights in the plane directed by the two first principal components.

    :param files_names: list
        list of the files paths to be parsed
    :param features: list
        features considered to represent the flights
    """
    ind = [f.split('/')[-1].split('.')[0] for f in files_names]
    df = pd.DataFrame(columns=features, index=ind)
    with open(config_path) as f_conf:
        config = json.load(f_conf)
    # Segmentation
    for f_name in files_names:
        print('parsing du fichier {}'.format(f_name))
        flight_data = txt_parser(f_name)
        intervals, _, ports_full_flight = segment(flight_data, config)
        weights_seg = get_weights(intervals, flight_data)
        weights_ports = get_weights(ports_full_flight, flight_data)
        weights = {}
        for d in [weights_seg, weights_ports]:
            weights.update(d)
        df.loc[f_name.split('/')[-1].split('.')[0]] = pd.Series(weights)

    # PCA
    print('Début de l\'ACP...')
    pca = PCA(n_components=2)
    pca.fit(df)
    var_ratio = pca.explained_variance_ratio_
    X = pca.fit(df).transform(df)
    V = pca.components_
    print(V)
    plt.figure(figsize=(10, 10))
    plt.title('''Représentation des vols dans le plan principal
    variance expliquée : {}'''.format(var_ratio))
    labels = [f.split('_')[-2] for f in ind]
    plt.plot(X[:, 0], X[:, 1], 'o')
    for label, x, y in zip(labels, X[:, 0], X[:, 1]):
        plt.annotate(label, xy=(x, y), xytext=(14, 20),
                     textcoords='offset points', ha='right', va='bottom',
                     bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.5),
                     arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    plt.show()

