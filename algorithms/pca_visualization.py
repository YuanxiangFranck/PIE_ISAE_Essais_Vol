#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 13:29:00 2017

@author: Florent Forest

ILIAD

PCA visualization of flight features on time segments

TO DO:
    * everything
    * tests
    * docstring
"""

# Standard imports
import time
import logging
# Modules imports
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import scale
from sklearn.decomposition import PCA
# Flight analysis functions import
from flight_analysis_fun import (extract_sl_window, get_feature_matrix,
                                 idx2date, idx2phase, idx2port)
import SignalData

def pca_visualization(flight_data=None, features=None, signal_categories=None,
                      signal_list=None, time_window='auto', n_segments='auto',
                      save=True, flight_name='undefined', out_dir='.',
                      out_filename='auto', show_plot=True, out_format='png',
                      conf=None):
    """
    TODO: docstring
    """
    # Handle arguments
    #if not isinstance(flight_data, SignalData.SignalData):
    #    logging.warning( 
    #    """The data argument must be a SignalData object containing the flight 
    #    data.""")
    #    return 
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
        if not s in flight_data.data.columns.values:
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
    feature_matrix = scale(feature_matrix)
    
    # PCA with visualization of flight phases
    reduced_data = PCA(n_components=2).fit_transform(feature_matrix)
    
    fig, ax = plt.subplots(1, 3)
    fig.set_figwidth(20)
    fig.set_figheight(10)

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

    colors = [phase_color_dic[phases[i]] for i in range(n_samples)]
    
    for col in phase_color_dic.items():
        p,c = col
        ax[0].scatter([reduced_data[i, 0] for i in range(n_samples) \
                     if colors[i] == c],
                    [reduced_data[i, 1] for i in range(n_samples) \
                     if colors[i] == c],
                    c=c, label=p, alpha=0.7, s=60)

    ax[0].legend(scatterpoints=1)
     
    for i in range(n_samples):
        ax[0].text(reduced_data[i, 0] + 0.2, reduced_data[i, 1], i)
    
    # PCA with visualization of ports

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

    colors = [port_color_dic[ports1[i]] for i in range(n_samples)]
    
    for col in port_color_dic.items():
        p,c = col
        ax[1].scatter([reduced_data[i, 0] for i in range(n_samples) if colors[i] == c], \
                    [reduced_data[i, 1] for i in range(n_samples) if colors[i] == c], \
                    c=c, label=p, alpha=0.7, s=60)

    ax[1].legend(scatterpoints=1)

    for i in range(n_samples):
        ax[1].text(reduced_data[i, 0] + 0.2, reduced_data[i, 1], i)
    
    # Side 2
    ports2 = []
    for i in range(n_samples):
        p = idx2port(flight_data.data.Time.iloc[0], flight_data.data.Time.iloc[-1],
                      flight_data.ports, i, sl_w, sl_s)
        if p:
            ports2.append(p[1][0])
        else:
            ports2.append('missing')

    colors = [port_color_dic[ports2[i]] for i in range(n_samples)]
    
    for col in port_color_dic.items():
        p,c = col
        ax[2].scatter([reduced_data[i, 0] for i in range(n_samples) if colors[i] == c], \
                    [reduced_data[i, 1] for i in range(n_samples) if colors[i] == c], \
                    c=c, label=p, alpha=0.7, s=60)

    ax[2].legend(scatterpoints=1)

    for i in range(n_samples):
        ax[2].text(reduced_data[i, 0] + 0.2, reduced_data[i, 1], i)
        
    ax[0].set_title("""
    - PCA Flight visualization -
    Features : {}
    Flight : {}
    Signals : {}
    Time window : {}
    """
    .format(features, flight_name, signal_categories, sl_w))
    ax[1].set_title('Side 1')
    ax[2].set_title('Side 2')
    
    if save:
        out_path = out_dir
        if out_dir[-1] != '/':
            out_path += '/'
        if out_filename == 'auto':
            t = time.localtime()
            out_path += 'pca_{}_{}_{}{}{}-{}{}{}.{}'\
            .format(flight_name, n_samples, t[2], t[1], t[0],
                    t[3], t[4], t[5], out_format)
        else:
            out_path += out_filename + '.' + out_format

        plt.savefig(out_path, bbox_inches='tight')
    
    if show_plot:
        plt.show()
        
if __name__ == '__main__':
    """
    from flight_analysis_fun import load_flight
    from flight_names import flight_names
    from signal_names import *
    flight_name = flight_names[0]
    path = '../../data/'
    data = SignalData.SignalData(load_flight(path+flight_name))
    
    conf = {'target_precisions_path': 'target_precisions.csv', 
            'regulation': signal_names_regul, 'target': target_names_regul,
            'binary': signal_names_bin, 'endogene': signal_names_endogene,
            'phases_colors': {'climb': 'r', 'cruise': 'b', 'landing': 'm',
                    'descent': 'g', 'hold': 'c', 'otg': 'y',
                    'take_off': 'k', 'missing': 'white'},
            'ports_colors': {'apu': 'g', 'ip1': 'c', 'ip2': 'b', 'hp1': 'orange',
             'hp2': 'r', 'no bleed': 'k', 'missing': 'white'}}
    """
    pca_visualization(flight_data=data, features=['mean', 'std', 'amplitude'],
            signal_categories=['regulation','endogene'], n_segments=100, 
            flight_name=flight_name, save=True, out_dir='../../Resultats/test/',
            show_plot=True, conf=conf)
    