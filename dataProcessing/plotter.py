"""
Script to plot data

TODO WARRNIG!!!!
This de not handle overlap in phases plot!
"""
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment
from data_info.units import units

def arguments_parser():
    import argparse
    from argparse import RawTextHelpFormatter
    import sys
    # Create parser
    decription = 'Script to plot some signals from data file'
    parser = argparse.ArgumentParser(description=decription, formatter_class=RawTextHelpFormatter)
    # Arguments
    parser.add_argument('txt_file', help='path to the text file (*.txt)')
    parser.add_argument('signals', nargs='*', help='names of the signals to plot')
    # Options
    parser.add_argument('-v', '--verbose', default=False, action="count",
                        help='Be more verbose\nNo option : warning level\n-v : info level\n -vv debug level')
    parser.add_argument('-l', '--list', default=False, action="store_true",
                        help='print the list of available signals to plot')
    # Parse the arguments
    arguments = parser.parse_args(sys.argv[1:])
    logging.debug('args : '+str(arguments))
    # Basic arguments handling: Verbose / out path
    level = logging.DEBUG
    if arguments.verbose == 1:
        level = logging.INFO
    elif arguments.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)
    return arguments


class Plotter:
    """
    Class to plot data from a txt file
    """
    def __init__(self, input_file=None):
        self.phases = None
        if input_file is None:
            self.data = pd.DataFrame()
        else:
            self.data = txt_parser(input_file)
            self.compute_phases()
        self.segments_color = {'climb': "r", 'cruise': "b",
                               'landing': 'm',
                               'descent': 'g', 'hold': "c",
                               'otg': 'y', 'take_off': 'k'}

    def set_data(self, data):
        "Set data of the plotter"
        self.data = data
        self.phases = segment(data)

    def compute_phases(self):
        "compute segmetation and convert intervall into index instead of time range"
        phases = segment(self.data)
        time = self.data.Time
        self.phases = {}
        for name, segments in phases.items():
            idx = np.zeros(time.size).astype(bool)
            for start, end in segments:
                idx = idx | ( (start < time) & (time < end ) )
            self.phases[name] = self.data.index[idx] # Was converted to pd.Series because of time

    def plot_phases(self, fig):
        "plot on a figure the flight phases"
        if "Time" not in self.data.columns:
            print("Time not in data cannot plot phase")
            return
        prev_phases = np.zeros(self.data.Time.size)
        for nb_phase, (name, idx) in enumerate(self.phases.items()):
            phases = prev_phases.copy()
            # Compute index of the phase
            phases[idx] = nb_phase + 1
            # Plot the phase
            fig.fill_between(self.data.Time, prev_phases, phases,
                             facecolor=self.segments_color[name], linewidth=0,
                             label=name, alpha=0.2)
            prev_phases = phases.copy()
        # Customize the y axis / labels for the phases
        fig.set_ylim(0, len(self.phases)+1)
        fig.grid()
        fig.legend(bbox_to_anchor=(1.02, 0.7, 1.1, 0), loc=2, ncol=1, mode="expand", borderaxespad=0.)

    def plot_data(self, signal1, signal2='Time', fig=plt):
        """
        Plot one data over a second data in a scatter cloud

        :param signal1: str
            name of the signal to plot
        :param [signal2='Time']: str
            if given it plot signal1 over signal2
        """
        # Check if each signal are in data
        if signal1 not in self.data.columns:
            print(signal1+"  not in data")
            return
        if signal2 not in self.data.columns:
            print(signal2+"  not in data")
            return
        if signal2 == "Time":
            signal2, signal1 = signal1, signal2
        fig.plot(self.data[signal1], self.data[signal2],
                 label=signal1+" / "+signal2)
        xlabel = "{} [{}]".format(signal1, units.get(signal1, ""))
        ylabel = "{} [{}]".format(signal2, units.get(signal2, ""))
        if fig == plt:
            fig.xlabel(xlabel)
            fig.ylabel(ylabel)
        else:
            fig.set_xlabel(xlabel)
            fig.set_ylabel(ylabel)
        # Add legend to the plot
        fig.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)


    def plot(self, signals):
        """
        Plot a list of signals

        :param signals: list
            List of signal name
        """
        _, host = plt.subplots()
        par = host.twinx()
        for name in signals:
            self.plot_data(name, fig=host)
        self.plot_phases(par)
        plt.show()


if __name__ == "__main__":
    # Parse arguments
    args = arguments_parser()
    # Parse the data
    logging.info("Read: "+ args.txt_file+"\n")

    plotter = Plotter(args.txt_file)
    plotter.plot(args.signals)
