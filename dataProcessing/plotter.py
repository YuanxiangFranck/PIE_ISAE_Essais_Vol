"""
Functions to plot data


See
* plot_data
* plot

Basic usage:

.. code-block:: python

    pp = Plotter("<path_to_file>")
    # Plot one signal
    pp.plot_data('WOW_FBK_AMSC1_CHA')
    # Plot multiple signals with phases
    pp.plot(['WOW_FBK_AMSC1_CHA', 'ADSP1 Pressure Altitude (feet)'])

Attributes:

phases:
    :type dict
    dictionnary with np.array with the indexes of the dataframe of each phases
:attr data: DataFrame
    pandas DataFrame containing the data
:attr segments_color: dict
    colors for each phases
"""

import logging

import numpy as np
import matplotlib.pyplot as plt
from dataProcessing.segmenter_utils import tuples_to_durations, get_weights
from data_info.units import units


SEGMENTS_ORDER = ["otg", "take_off", "landing", "climb", "descent", "hold", "cruise"]

def compute_phases_idx(phases, time):
    """
    Compute segmetation and convert intervals into index instead of time range
    """
    phases_idx = {}
    for name, segments in phases.items():
        idx = np.zeros(time.size).astype(bool)
        for start, end in segments:
            idx = idx | ( (start < time) & (time < end ) )
        phases_idx[name] = time.index[idx] # Was converted to pd.Series because of time
    return phases_idx

def plot_phases(time, flight_phases_idx, phases_colors, fig=plt):
    """
    Plot on a figure the flight phases
    see the attribut segments_color for color selection

    :param time: pd.Series
        time series with time
    :param flight_phases_idx: dict
        dict with phases as key and Series of bool (True if in phase)
    :param fig: AxesSubplot
        axes subplot (using twinx) to plot phases on another y axis
    """
    prev_phases = np.zeros(time.size)
    for nb_phase, name in enumerate(SEGMENTS_ORDER):
        idx = flight_phases_idx[name]
        phases = prev_phases.copy()
        # Compute index of the phase
        phases[idx] = nb_phase + 1
        # Plot the phase
        fig.fill_between(time, prev_phases, phases,
                         facecolor=phases_colors[name], linewidth=0,
                         label=name, alpha=0.2)
        prev_phases = phases.copy()
    # Customize the y axis / labels for the phases

    fig.grid()
    yticks_label = [""] + SEGMENTS_ORDER
    if fig == plt:
        fig.ylim((0, len(flight_phases_idx)+1))
        fig.yticks(np.arange(len(flight_phases_idx)+1), yticks_label)
        plt.show()
    else:
        fig.set_ylim(0, len(flight_phases_idx)+1)
        fig.set_yticklabels(yticks_label)


def plot_data(data, signal1, signal2='Time', fig=plt):
    """
    Plot one data over a second data in a scatter cloud
    :param data: pd.DataFrame
        dataFrame with data to plot
    :param signal1: str
        name of the signal to plot
    :param [signal2='Time']: str
        if given it plot signal1 over signal2
    :param [fig = plt ] : pyplot | AxesSubplot
        by default plot using pyplot
        This attribute is used for muliple y axis plot
    """
    # Check if each signal are in data
    if signal1 not in data.columns:
        logging.warn(signal1+"  not in data")
        return
    if signal2 not in data.columns:
        logging.warn(signal2+"  not in data")
        return
    if signal2 == "Time":
        signal2, signal1 = signal1, signal2
    fig.plot(data[signal1], data[signal2],
             label=signal1+" / "+signal2)
    xlabel = "{} [{}]".format(signal1, units.get(signal1, ""))
    ylabel = "{} [{}]".format(signal2, units.get(signal2, ""))
    if fig == plt:
        # Case of basic plots without phase (using plt)
        fig.xlabel(xlabel)
        fig.ylabel(ylabel)
    else:
        # Case of plot in AxesSubplot
        fig.set_xlabel(xlabel)
        fig.set_ylabel(ylabel)
    # Add legend to the plot
    fig.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0.)


def plot(data, phases_idx, signals):
    """
    Plot a list of signals

    :param data: pd.DataFrame
        dataFrame with data to plot
    :param phases_idx: dict
        dict with phases as key and Series of bool (True if in phase)
    :param signals: list
        List of signal name
    """
    _, host = plt.subplots()
    par = host.twinx()
    for name in signals:
        plot_data(data, name, fig=host)
    plot_phases(data.Time, phases_idx, par)
    plt.show()


def plot_segments_pie(seg, data, phases_colors):
    """
    Plot a pie chart of the percentage of time spent on each segment
    :param seg: dict
        dict with list of start, end for each segment
    :param data: pd.DataFrame
        the data
    """
    weights = get_weights(seg, data)
    plt.figure(1, figsize=(10, 10))
    labels = list(weights.keys())
    fracs = [weights[key] for key in labels]
    sum_weight = sum(weight for weight in fracs)
    if sum_weight < 1:
        fracs.append(1 - sum_weight)
        labels.append('no segment')
    plot_colors = [phases_colors[name] for name in labels]
    plt.pie(fracs, labels=labels, colors=plot_colors, autopct='%1.1f%%')
    plt.title('Temps passé dans chaque phase, en pourcentage de la durée du vol', bbox={'facecolor':'0.8', 'pad':5})
    plt.draw()


def plot_ports_seg(raw_ports, ports_colors):
    """
    For each phase, plot one pie chart for each side of the time spent on each port

    :param ports: dict
        ports usage for each segments
    """
    ports = {}
    for each_segment, ports_on_segment in raw_ports.items():
        ports[each_segment] = tuples_to_durations(ports_on_segment)
    f, axarr = plt.subplots(2, 7, figsize=(23, 7))
    f.suptitle('Utilisation des ports selon chaque phase', bbox={'facecolor':'0.8', 'pad':5})
    j = 0
    for each_segment in ports:
        labels = ports[each_segment].keys()  # pressure ports names
        # left pressure ports + apu
        labels_1 = [l for l in labels if l[-1] == '1'] + ['apu', 'no bleed']
        # right pressure ports + apu
        labels_2 = [l for l in labels if l[-1] == '2'] + ['apu', 'no bleed']
        fracs_1 = [ports[each_segment][key] for key in labels_1]
        fracs_2 = [ports[each_segment][key] for key in labels_2]
        colors_1 = [ports_colors[name] for name in labels_1]
        colors_2 = [ports_colors[name] for name in labels_2]
        axarr[0, j].pie(fracs_1, labels=labels_1, colors=colors_1, autopct='%1.1f%%')
        axarr[0, j].set_title('{} côté 1'.format(each_segment), bbox={'facecolor':'0.8', 'pad':5})
        axarr[1, j].pie(fracs_2, labels=labels_2, colors=colors_2, autopct='%1.1f%%')
        axarr[1, j].set_title('{} côté 2'.format(each_segment), bbox={'facecolor':'0.8', 'pad':5})
        j = (j+1)%7
    plt.show()


def plot_ports_sides(ports_full_flight, ports_colors):
    """
    Plot one pie chart for each side of the time spent on each port

    :param ports_full_flight: dict
        port usage on full filght
    """
    ports_durations = tuples_to_durations(ports_full_flight)
    _, axarr = plt.subplots(1, 2, figsize=(20, 10))
    labels = ports_durations.keys()  # pressure ports names
    for side in [1, 2]:
        labels_1 = [l for l in labels if l[-1] == str(side)] + ['apu', 'no bleed']
        fracs_1 = [ports_durations[key] for key in labels_1]
        plot_colors = [ports_colors[name] for name in labels_1]
        axarr[side-1].pie(fracs_1, labels=labels_1, autopct='%1.1f%%',
                          colors=plot_colors)
        axarr[side-1].set_title('côté '+str(side), bbox={'facecolor':'0.8', 'pad':5})
    plt.show()


def plot_ports(ports_full_flight, data, ports_colors):
    """
    Plot a pie chart of the percentage of time spent on each pressure port

    :param ports_full_flight: dict
        ports usage for the whole flight
    :param data: DataFrame
        data of the flight
    """
    flight_duration = data.Time.iloc[-1] - data.Time.iloc[0]
    ports_durations = tuples_to_durations(ports_full_flight)
    # Convert durations on each port into percentage of the flight duration
    for port in ports_durations.keys():
        ports_durations[port] /= flight_duration
    plt.figure(1, figsize=(10, 10))
    labels = ports_durations.keys()
    fracs = [ports_durations[key] for key in labels]
    colors = [ports_colors[name] for name in labels]
    plt.pie(fracs, labels=labels, colors=colors, autopct='%1.1f%%')
    plt.title('Temps passé sur chaque port, en pourcentage de la durée du vol', bbox={'facecolor':'0.8', 'pad':5})
    plt.show()
