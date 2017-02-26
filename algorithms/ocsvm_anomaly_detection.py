# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 14:01:52 2017

@author: Florent Forest

ILIAD

OCSVM anomaly detection on time segments

TO DO:
    * everything
    * tests
    * docstring
"""

# Standard imports
import time
import logging
# Modules imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import gridspec
from matplotlib.lines import Line2D
import seaborn as sns
# Flight analysis functions import
from flight_analysis_fun import (extract_sl_window, extract_sl_window_delta, 
get_feature_matrix, idx2date, idx2phase, idx2port)
from SignalData import SignalData

def ocsvm_detection(data=None, features=None, signal_categories=None,
                    signal_list=None, gamma=0.1, nu=0.3, time_window='auto',
                    n_segments='auto', hclust=False, save=True, report=True,
                    flight_name='undefined', out_dir='.', out_filename='auto',
                    show_plot=True, out_format='pdf', conf=None):
    """
    TODO: docstring
    """
    # Handle arguments
    if not isinstance(data, pd.core.frame.DataFrame):
        logging.warning( 
        """The data argument must be a pandas DataFrame 
        containing the flight data.""")
        return 
    if not features:
        logging.warning( 
        """No features selected. The features argument must be a list of 
        strings. Refer to documentation for a list of available features.""")
        return
    if not signal_categories:
        logging.warning( 
        """No signal categories selected. The signal_categories argument must 
        be either a list of strings corresponding to a signal categories, or 
        'custom'. Signal categories are defined in the configuration file.""")
    if signal_categories == 'custom' and not signal_list:
        logging.warning( 
        """The signal_categories argument is set to 'custom', but no signal list
        is selected. The signal_list argument must be set to a list of signal 
        names. Signal names are defined in the configuration file.""")
        return 
    if time_window == 'auto' and n_segments == 'auto':
        logging.warning( 
        """The arguments time_window and n_segments cannot both be set to 
        'auto'. One of them must be specified.""")
    if time_window != 'auto' and n_segments != 'auto':
        logging.warning( 
        """The arguments time_window and n_segments cannot both be set to a 
        value. One of them must be left to 'auto'.""")
    if not conf:
        logging.warning( 
        """No configuration specified ! The conf argument must be set to the 
        current configuration object.""")
    
    # Initialize variables
    anomalies = {}
    
    # Load data into SignalData object
    flight_data = SignalData(data)
    
    # Compute flight phases and ports
    flight_data.compute_flight_segmentation()

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
        
    # Set selected signals
    if signal_categories == 'custom':
        # Use signal list given in argument
        selected_signals = signal_list
    else:
        # Concatenate signals in categories
        selected_signals = sum((conf[cat] for cat in signal_categories), [])
    
    # Remove signals which are not present in the flight data
    selected_signals_copy = selected_signals.copy()
    cc = 0
    for s in selected_signals_copy:
        if not s in data.columns.values:
            cc += 1
            selected_signals.remove(s)
    if cc > 0:
        logging.warning('Removed {}/{} signals not present in flight data.'
                    .format(cc, len(selected_signals_copy)))
    del selected_signals_copy
    
    # Cut signal into samples with a sliding window
    samples = extract_sl_window(flight_data.data, selected_signals, 
                                sl_w, sl_s)
    # Extract features
    feature_matrix = get_feature_matrix(samples, features, 
                                        normalized=False)
    
    # Scale features
    from sklearn.preprocessing import scale
    feature_matrix = scale(feature_matrix)
    
    # Apply OCSVM
    from sklearn import svm
    ocsvm = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    
    # ...on all signals
    ocsvm.fit(feature_matrix)
    predictions = ocsvm.predict(feature_matrix)
    anomalies['global'] = (predictions == -1)

    # ...individually on the signals grouped by AMSC and CH
    signal_prefix = list(set((s.split('_AMSC')[0] for s in selected_signals)))
    signal_suffix = list('_AMSC{}_CH{}'.format(x,y) for x in [1,2]
                         for y in ['A','B'])
    
    for prefix in signal_prefix:
        ps_selected_signals = [prefix + suffix for suffix in signal_suffix]
        # Cut signal into samples with a sliding window
        ps_samples = extract_sl_window(flight_data.data, ps_selected_signals,
                                       sl_w, sl_s)
        # Extract features
        ps_feature_matrix = get_feature_matrix(ps_samples, features,
                                               normalized=False)
        # Scale features
        ps_feature_matrix = scale(ps_feature_matrix)
    
        ocsvm.fit(ps_feature_matrix)
        ps_predictions = ocsvm.predict(ps_feature_matrix)
    
        anomalies[prefix] = (ps_predictions == -1)
    
    # Set ylabels
    ylabels = ['global'] + signal_prefix

    # Generate anomaly heatmap
    anomaly_matrix = np.zeros((len(signal_prefix)+1, n_samples))

    anomaly_matrix[0,:] = anomalies['global']
    
    for i,s in enumerate(signal_prefix):
        for j in range(n_samples):
            anomaly_matrix[i+1,j] = anomalies[s][j]
    
    # Perform hierarchical clustering on lines (except first line 'global')
    if hclust:

        from scipy.cluster.hierarchy import dendrogram
        from sklearn.cluster import AgglomerativeClustering

        hclust = AgglomerativeClustering()
        hclust = hclust.fit(anomaly_matrix[1:,:])

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
        # Increment leaves indices because we do not cluster on the firest line
        leaves = [l+1 for l in leaves]

        # Re-organize feature matrix and tick labels
        anomaly_matrix[1:,:] = anomaly_matrix[leaves,:]
        ylabels = ['global'] + [ylabels[i] for i in leaves]

    # Create time labels
    origin = flight_data.data.Time.iloc[0]
    end = flight_data.data.Time.iloc[-1]
    xlabels = [idx2date([(origin,end)], idx, sl_w, 
                        sl_s) for idx in range(n_samples)]
    
    # Prepare display of flight phases
    # TODO: use conf
    phase_color_dic = {'climb': 'r', 'cruise': 'b', 'landing': 'm', \
                        'descent': 'g', 'hold': 'c', 'otg': 'y', \
                        'take_off': 'k', 'missing': 'white'}
    
    phases = []
    for i in range(n_samples):
        p = idx2phase(data.Time.iloc[0], data.Time.iloc[-1], 
                      flight_data.flight_segments, i, sl_w, sl_s)
        if p:
            phases.append(p[0])
        else:
            phases.append('missing')

    phase_cmap = ListedColormap([phase_color_dic[phases[i]]
                                 for i in range(n_samples)])

    # Prepare display of ports
    # TODO: use conf
    port_color_dic = {'apu': 'g', 'ip1': 'c', 'ip2': 'b', 'hp1': 'orange', \
                 'hp2': 'r', 'no bleed': 'k', 'missing': 'white'}
    
    # Side 1
    ports1 = []
    for i in range(n_samples):
        p = idx2port(data.Time.iloc[0], data.Time.iloc[-1],
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
        p = idx2port(data.Time.iloc[0], data.Time.iloc[-1],
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
    n_heatmaps = anomaly_matrix.shape[0]//n_sig
    
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
        sns.heatmap(anomaly_matrix[start:stop], xticklabels=xlabels, 
                    yticklabels=ylabels[start:stop], annot=False, ax=ax2, 
                    cmap='Reds')
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
        - OCSVM Anomaly heatmap (nu={}, gamma={}) -
        Features : {}
        Flight : {}
        Signals : {}
        Time window : {}
        """
        .format(nu, gamma, features, flight_name, signal_categories, sl_w))
        
        if save:
            out_path = out_dir
            if out_dir[-1] != '/':
                out_path += '/'
            if out_filename == 'auto':
                t = time.localtime()
                out_path += 'anomaly_hm_{}_{}_{}{}{}-{}{}{}_{}.{}'\
                .format(flight_name, n_samples, t[2], t[1], t[0],
                        t[3], t[4], t[5], k, out_format)
            else:
                out_path += out_filename + '_' + str(k) + '.' + out_format
    
            plt.savefig(out_path, bbox_inches='tight')
        
        if show_plot:
            plt.show()
            plt.clf()
    
    # Generate heatmaps
    if n_heatmaps == 0:
        create_heatmap(0, 0, anomaly_matrix.shape[0])
    else:
        for k in range(n_heatmaps):
            create_heatmap(k, k*n_sig, (k+1)*n_sig)
        # Make last heatmap if needed
        create_heatmap(k+1, (k+1)*n_sig, anomaly_matrix.shape[0])
    
    # Generate anomaly report in csv file
    if report:
        report = {}
        report['Time frame'] = xlabels
        report['Phase'] = phases
        report['Anomaly'] = anomalies['global']
        # TODO: anomaly score
        #report['Anomaly score'] = [sum(anomalies[s][i] for s in signal_prefix) \
        #                           for i in range(n_samples)]
        report['Anomalous signals'] = \
        [', '.join([s for s in signal_prefix if anomalies[s][i]]) 
        for i in range(n_samples)]

        out_path = out_dir
        if out_dir[-1] != '/':
            out_path += '/'
        if out_filename == 'auto':
            t = time.localtime()
            out_path += 'anomaly_report_{}_{}_{}{}{}-{}{}{}.csv'\
            .format(flight_name, n_samples, t[2], t[1], t[0],
                    t[3], t[4], t[5])
        else:
            out_path += out_filename + '.csv'
    
        pd.DataFrame(report).to_csv(out_path,
        columns = ['Time frame', 'Phase', 'Anomaly', 'Anomaly score',
        'Anomalous signals'], index_label = 'Time Id')
        
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

    ocsvm_detection(data=data, features=['mean', 'std', 'amplitude'],
            signal_categories=['regulation','endogene'], n_segments=100, 
            flight_name=flight_name, hclust=True, save=True, report=True,
            out_dir='../../Resultats/test/', show_plot=False, conf=conf)
    