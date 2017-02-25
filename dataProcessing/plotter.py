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

from data_info.units import units


SEGMENTS_COLOR = {'climb': "r", 'cruise': "b", 'landing': 'm', 'descent': 'g',
                  'hold': "c", 'otg': 'y', 'take_off': 'k'}
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

def plot_phases(time, flight_phases_idx, fig=plt):
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
                         facecolor=SEGMENTS_COLOR[name], linewidth=0,
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
