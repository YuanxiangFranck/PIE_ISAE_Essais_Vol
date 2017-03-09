# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 14:01:52 2017

@author: Florent Forest

ILIAD

Heatmap visualization of features on time segments

TO DO:
    * docstring
"""

# Standard imports
import time
import logging
# Modules imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import gridspec
from matplotlib.lines import Line2D
import seaborn as sns
# Flight analysis functions import
from algorithms.flight_analysis_fun import (extract_sl_window, extract_sl_window_delta,
                                 get_feature_matrix, idx2date, idx2phase,
                                 idx2port)
from algorithms.SignalData import SignalData

def heatmap(flight_data=None, feature=None, signal_category=None, signal_list=None,
            time_window='auto', n_segments='auto', hclust=False, save=True,
            flight_name='undefined', out_dir='.', out_filename='auto',
            show_plot=True, out_format='pdf', annot=False, robust=True,
            conf=None):
    """
    TODO: docstring
    """

    # Handle arguments
    if not isinstance(flight_data, SignalData):
        logger.error(
        "The signal_data argument must be a instance of the SignalData class containing the flight data.")
        return
    if not feature:
        logger.error(
        "No feature selected. The feature argument must be a string. Refer to documentation for a list of available features.")
        return
    if not signal_category:
        logger.error(
        "No signal category selected. The signal_category argument must be either a string corresponding to a signal category, or 'custom'. Signal categories are defined in the configuration file.")
        return
    if signal_category == 'custom' and not signal_list:
        logger.error(
        "The signal_category argument is set to 'custom', but no signal list"
        "is selected. The signal_list argument must be set to a list of signal"
        "names. Signal names are defined in the configuration file.")
        return
    if time_window == 'auto' and n_segments == 'auto':
        logger.error(
        "The arguments time_window and n_segments cannot both be set to 'auto'. One of them must be specified.")
        return
    if time_window != 'auto' and n_segments != 'auto':
        logger.error(
        "The arguments time_window and n_segments cannot both be set to a value. One of them must be left to 'auto'.")
        return
    if not conf:
        logger.error(
        "No configuration specified ! The conf argument must be set to the current configuration object.")
        return

    # Initialize variables
    use_targets = False
    features = []

    # Set sliding window parameters
    if n_segments != 'auto':
        # Assert that the number of segments is positive
        assert(n_segments > 0)

        n_samples = n_segments
        sl_w = len(flight_data.data)//n_samples
        # Using a stride is not used yet, but can be easly implemented
        sl_s = sl_w
    else:
        # Assert that the time window is positive
        assert(time_window > 0)

        sl_w = time_window
        # Using a stride is not used yet, but can be easly implemented
        sl_s = sl_w
        n_samples = len(flight_data.data)//sl_w

    # Manage specific heatmap types
    if feature == 'percent_time_off_regulation':
        use_targets = True
        # Load signal names
        selected_signals = conf['regulation']
        target_signals = conf['target']

        # Set ylabels
        ylabels = sorted(selected_signals)

        # Set features
        features = ['percent_time_over_threshold']
    elif feature == 'time_off_regulation':
        use_targets = True
        # Load signal names
        selected_signals = conf['regulation']
        target_signals = conf['target']

        # Set ylabels
        ylabels = sorted(selected_signals)

        # Set features
        features = ['time_over_threshold']
    elif feature == 'off_regulation_crossings':
        use_targets = True
        # Load signal names
        selected_signals = conf['regulation']
        target_signals = conf['target']

        # Set ylabels
        ylabels = sorted(selected_signals)

        # Set features
        features = ['threshold_crossings']
    else:
        if signal_category == 'custom':
            # Use signal list given in argument
            selected_signals = signal_list
        else:
            selected_signals = conf[signal_category]

        # Set ylabels
        ylabels = selected_signals
        # Set features
        features = [feature]

    # Remove signals which are not present in the flight data
    selected_signals_copy = selected_signals.copy()
    cc = 0
    for s in selected_signals_copy:
        if s not in flight_data.data.columns:
            cc += 1
            selected_signals.remove(s)
    if cc > 0:
        logging.warning('Removed {}/{} signals not present in flight data.'
                    .format(cc, len(selected_signals_copy)))
    del selected_signals_copy

    if use_targets:
        # Load target precisions
        target_precisions = pd.read_csv(conf['target_precisions_path'],
                                        header=0, sep=',')

        thresholds = target_precisions['Precision'].as_matrix()
        delta_type = target_precisions['Type'].as_matrix()

        # Compute deltas and cut signal into samples with a sliding window
        samples = extract_sl_window_delta(flight_data.data, selected_signals,
                                          target_signals, sl_w, sl_s,
                                          delta_type)

        # Extract features
        feature_matrix = get_feature_matrix(samples, features,
                                            normalized=False,
                                            threshold=thresholds)

    else:
        # Cut signal into samples with a sliding window
        samples = extract_sl_window(flight_data.data, selected_signals,
                                    sl_w, sl_s)
        # Extract features
        feature_matrix = get_feature_matrix(samples, features,
                                            normalized=False)

    # Preprocessing for binary transitions heatmap
    if feature == 'nb_transitions':
        non_zero_signal_idx = []

        for i in range(feature_matrix.shape[1]):
            if (feature_matrix[:,i] != 0).any():
                non_zero_signal_idx.append(i)

        feature_matrix = feature_matrix[:,non_zero_signal_idx]

        non_zero_signal_names = []
        for idx in non_zero_signal_idx:
            non_zero_signal_names.append(selected_signals[idx])

        # Trier les signaux par nb de changements
        ordre = np.argsort(-np.sum(feature_matrix, axis=0))

        feature_matrix = feature_matrix[:,ordre]
        for i in range(len(non_zero_signal_names)):
            non_zero_signal_names[i] = non_zero_signal_names[ordre[i]]

        selected_signals = non_zero_signal_names

        # Set ylabels
        ylabels = selected_signals

    # Perform hierarchical clustering on signals
    if hclust:

        from scipy.cluster.hierarchy import dendrogram
        from sklearn.cluster import AgglomerativeClustering

        hclust = AgglomerativeClustering()
        hclust = hclust.fit(feature_matrix.T)

        # Distances between each pair of children
        # Since we don't have this information, we can use a uniform one for plotting
        distance = np.arange(hclust.children_.shape[0])

        # The number of observations contained in each cluster level
        no_of_observations = np.arange(2, hclust.children_.shape[0]+2)

        # Create linkage matrix
        linkage_matrix = np.column_stack([hclust.children_, distance,
                                          no_of_observations]).astype(float)

        # Get the dendrogram leaves
        leaves = dendrogram(linkage_matrix, no_plot=True)['leaves']

        # Re-organize feature matrix and tick labels
        feature_matrix = feature_matrix[:,leaves]
        ylabels = [ylabels[i] for i in leaves]

    # Create time labels
    origin = flight_data.data.Time.iloc[0]
    end = flight_data.data.Time.iloc[-1]
    xlabels = [idx2date([(origin,end)], idx, sl_w,
                        sl_s) for idx in range(n_samples)]

    # Prepare display of flight phases
    phase_color_dic = conf['phases_colors']

    phases = []
    for i in range(n_samples):
        p = idx2phase(flight_data.data.Time.iloc[0],
                      flight_data.data.Time.iloc[-1],
                      flight_data.flight_segments, i, sl_w, sl_s)
        if p:
            phases.append(p[0])
        else:
            phases.append('missing')

    phase_cmap = ListedColormap([phase_color_dic[phases[i]]
                                 for i in range(n_samples)])

    # Prepare display of ports
    port_color_dic = conf['ports_colors']

    # Side 1
    ports1 = []
    for i in range(n_samples):
        p = idx2port(flight_data.data.Time.iloc[0],
                     flight_data.data.Time.iloc[-1],
                     flight_data.ports, i, sl_w, sl_s)
        if p:
            ports1.append(p[0][0])
        else:
            ports1.append('missing')

    port1_cmap = ListedColormap([port_color_dic[ports1[i]]
                                for i in range(n_samples)])
    # Side 2
    ports2 = []
    for i in range(n_samples):
        p = idx2port(flight_data.data.Time.iloc[0], flight_data.data.Time.iloc[-1],
                      flight_data.ports, i, sl_w, sl_s)
        if p:
            ports2.append(p[1][0])
        else:
            ports2.append('missing')

    port2_cmap = ListedColormap([port_color_dic[ports2[i]]
                                for i in range(n_samples)])

    # Create heatmap figures

    # Number of signals per heatmap
    n_sig = 50
    # Number of heatmaps to generate
    n_heatmaps = len(selected_signals)//n_sig

    def create_heatmap(k, start, stop):

        if stop <= start:
            return

        fig = plt.figure(figsize=(10*n_samples//20,10))
        gs = gridspec.GridSpec(4, 1, height_ratios=[1, 1, 1, 50])

        # Phases
        ax0 = plt.subplot(gs[0])
        ax0.imshow(np.arange(n_samples).reshape(1,-1), cmap=phase_cmap,
                   interpolation='nearest')
        ax0.set_axis_off()
        ax0.grid(False)

        # Ports
        # Side 1
        ax11 = plt.subplot(gs[1])
        ax11.imshow(np.arange(n_samples).reshape(1,-1), cmap=port1_cmap,
                   interpolation='nearest')
        ax11.set_axis_off()
        ax11.grid(False)

        # Side 2
        ax12 = plt.subplot(gs[2])
        ax12.imshow(np.arange(n_samples).reshape(1,-1), cmap=port2_cmap,
                   interpolation='nearest')
        ax12.set_axis_off()
        ax12.grid(False)

        ax2 = plt.subplot(gs[3])
        sns.heatmap(feature_matrix.T[start:stop], xticklabels=xlabels,
                    yticklabels=ylabels[start:stop], annot=annot, ax=ax2,
                    robust=robust)
        # Set tick labels direction
        plt.yticks(rotation=0)
        plt.xticks(rotation=90)

        box0 = ax0.get_position()
        box2 = ax2.get_position()

        ax0.set_position([box2.x0, box0.y1-0.095, box2.x1-box2.x0, 0.04])
        ax11.set_position([box2.x0, box0.y1-0.125, box2.x1-box2.x0, 0.04])
        ax12.set_position([box2.x0, box0.y1-0.150, box2.x1-box2.x0, 0.04])

        create_proxy = lambda c: Line2D([0],[0],color=c,marker='s',linestyle='None')

        phase_proxies = [create_proxy(color) for color in phase_color_dic.values()]
        fig.legend(phase_proxies, phase_color_dic.keys(), numpoints=1, markerscale=2, \
                   loc=(0.89,0.695), ncol=1)

        port_proxies = [create_proxy(color) for color in port_color_dic.values()]
        fig.legend(port_proxies, port_color_dic.keys(), numpoints=1, markerscale=2, \
                   loc=(0.89,0.495), ncol=1)

        ax0.set_title("""
        - {} -
        Flight : {}
        Signals : {}
        Time window : {}
        """
        .format(feature, flight_name, signal_category, sl_w))

        if save:
            out_path = out_dir
            if out_dir[-1] != '/':
                out_path += '/'
            if out_filename == 'auto':
                t = time.localtime()
                out_path += 'hm_{}_{}_{}_{}{}{}-{}{}{}_{}.{}'.format(flight_name,
                feature, n_samples, t[2], t[1], t[0], t[3], t[4], t[5], k,
                out_format)
            else:
                out_path += out_filename + '_' + str(k) + '.' + out_format

            plt.savefig(out_path, bbox_inches='tight')

        if show_plot:
            plt.show()
            plt.clf()

    # Generate heatmaps
    for k in range(n_heatmaps):
        create_heatmap(k, k*n_sig, (k+1)*n_sig)

    # Make last heatmap if needed
    create_heatmap(k+1, (k+1)*n_sig, len(selected_signals))


if __name__ == '__main__':

    from flight_analysis_fun import load_flight
    from flight_names import flight_names
    from signal_names import *
    flight_name = flight_names[0]
    path = '../../data/'
    data = load_flight(path+flight_name)

    conf = {'target_precisions_path': 'target_precisions.csv',
            'regulation': signal_names_regul, 'target': target_names_regul,
            'binary': signal_names_bin, 'endogene': signal_names_endogene}

    signal_data = SignalData(data)
    signal_data.compute_flight_segmentation()
    heatmap(flight_data=signal_data, feature='off_regulation_crossings',
            signal_category='regulation', n_segments=50,
            flight_name=flight_name, hclust=True,
            out_dir='../../Resultats/test/', show_plot=False, conf=conf)
