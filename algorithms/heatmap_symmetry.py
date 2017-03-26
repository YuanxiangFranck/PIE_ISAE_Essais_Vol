# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 13:55:31 2017

@author: Matthieu
"""

# Standard imports
import time
# Modules imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import gridspec
from matplotlib.lines import Line2D
import seaborn as sns
# Flight analysis functions import
from algorithms.flight_analysis_fun import (extract_sl_window, idx2date, idx2phase,
                                 idx2port)
from algorithms.SignalData import SignalData
from algorithms.Symmetry import SymmetryTest
from dataProcessing.utils import logger

def heatmap_symmetry(flight_data=None, error=0.01, time_window='auto', n_segments='auto',
                     hclust=False, save=True, flight_name='undefined',
                     signals1 = None, signals2 = None, type_signals = '',
                     out_dir='.', out_filename='auto', show_plot=True,
                     out_format='pdf', conf=None):

    """
    Computes the relative time of anomaly on each time segment of a flight,
    and exports it as a heatmap visualization to a file.
    The result can be split across several files. A clustering option can be activated.

    :param flight_data: SignalData object
        Flight data

    :param error: int
        The relative error threshold

    :param time_window: int
        Length of the time window used to cut the flight into time segments, or 'auto' if n_segments is used instead

    :param n_segments: int
        Number of time segments used to cut the flight, or 'auto' if time_window is used instead

    :param hclust: boolean
        Apply hierarchical clustering to group similar signals

    :param save: boolean
        Save heatmap to a file

    :param flight_name: string
        Name of the flight

    :param signals1: list of string
        List of the names of the first column of signals to compare (the first name of each pair)

    :param signals2: list of string
        List of the names of the second column of signals to compare (the second name of each pair)

    :param type_signal: string
        "Channel" or "Lateral", depends on the considerated pair

    :param out_dir: string
        Directory where the exported files will be saved

    :param out_filename: string
        Filename of the exported files, or 'auto' to generate an automatic filename

    :param show_plot: boolean
        Display figure in the python shell

    :param out_format: string
        'pdf' by default, or image format (i.e. 'png')

    :param conf: dict
        Configuration

    """

    if time_window == 'auto' and n_segments == 'auto':
        logger.error(
        "The arguments time_window and n_segments cannot both be set to 'auto'. One of them must be specified.")
        return
    if time_window != 'auto' and n_segments != 'auto':
        logger.error(
        "The arguments time_window and n_segments cannot both be set to a value. One of them must be left to 'auto'.")
        return

    assert(len(signals1)==len(signals2))


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


    ylabels = signals1

    # Cut signal into samples with a sliding window
    samples_signals1 = extract_sl_window(flight_data.data, signals1,
                                         sl_w, sl_s, n_samples)
    samples_signals2 = extract_sl_window(flight_data.data, signals2,
                                         sl_w, sl_s, n_samples)


    asymmetry_matrix = np.zeros((len(signals1),n_samples))
    binary_names = conf["binary"]

    for i in range(n_samples):
        for j in range(len(signals1)):
            signal1 = samples_signals1[i].data.iloc[:,j]
            signal2 = samples_signals2[i].data.iloc[:,j]
            res = SymmetryTest(signal1, signal2, error, binary_names, signals1[j], "none")
            asymmetry_matrix[j,i] = len(res[1][:])/sl_w # time indexes of anomalies/length of the time window

    # Perform hierarchical clustering on signals
    if hclust:

        from scipy.cluster.hierarchy import dendrogram
        from sklearn.cluster import AgglomerativeClustering

        hclust = AgglomerativeClustering()
        hclust = hclust.fit(asymmetry_matrix)

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
        asymmetry_matrix = asymmetry_matrix[leaves,:]
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
    n_heatmaps = len(signals1)//n_sig

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
        sns.heatmap(asymmetry_matrix[start:stop], xticklabels=xlabels,
                    yticklabels=ylabels[start:stop], ax=ax2)
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
        - Asymmetry Heatmap for {} symmetry -
        relative error used : {}
        Flight : {}
        Time window : {}
        """
        .format(type_signals, error, flight_name, sl_w))

        if save:
            out_path = out_dir
            if out_dir[-1] != '/':
                out_path += '/'
            if out_filename == 'auto':
                t = time.localtime()
                out_path += 'hm_{}_symmetry_{}_error_{}_{}_{}{}{}-{}{}{}_{}.{}'.format(flight_name,
                type_signals, error, n_samples, t[2], t[1], t[0], t[3], t[4], t[5], k,
                out_format)
            else:
                out_path += out_filename + '_' + str(k) + '.' + out_format

            plt.savefig(out_path, bbox_inches='tight')

        if show_plot:
            plt.show()
        plt.close(fig)

    # Generate heatmaps
    if n_heatmaps == 0:
        create_heatmap(0, 0, asymmetry_matrix.shape[0])
    else:
        for k in range(n_heatmaps):
            create_heatmap(k, k*n_sig, (k+1)*n_sig)
        # Make last heatmap if needed
        create_heatmap(k+1, (k+1)*n_sig, asymmetry_matrix.shape[0])
