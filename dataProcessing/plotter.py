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


    def compute_phases(self):
        "compute segmetation and convert intervall into index instead of time range"
        phases = segment(self.data)
        time = self.data.Time
        self.phases = {name: np.zeros(time.size).astype(bool) for name in phases}
        for name, segments in phases.items():
            idx = self.phases[name]
            for start, end in segments:
                idx = idx | ( (start < time) & (time < end ) )
            self.phases[name] = idx # Was converted to pd.Series because of time

    def plot_data(self, signal1, signal2='Time', plot_phases=True):
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
        plt.plot(self.data[signal1], self.data[signal2],
                 label=signal1+" / "+signal2)
        plt.xlabel("{} [{}]".format(signal1, units.get(signal1, "")))
        plt.ylabel("{} [{}]".format(signal2, units.get(signal2, "")))
        # Plot phases
        if plot_phases:
            if "Time" not in self.data.columns:
                print("Time not in data cannot plot phase")
            phases = np.zeros(self.data[signal1].size)
            legend = {}
            for nb_phase, (name, bool_idx) in enumerate(self.phases.items()):
                # Compute index of the phase
                idx = self.data.index[bool_idx]
                phases[idx] = nb_phase+1
                legend[name] = nb_phase+1
            # Plot the phase
            plt.plot(self.data[signal1], phases, label="phases", linestyle="dashed")
        # Add legend to the plot
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)


    def set_data(self, data):
        "Set data of the plotter"
        self.data = data
        self.phases = segment(data)


    def plot(self, signals):
        """
        Plot a list of signals

        :param signals: list
            List of signal name
        """
        plot_phases = True
        for name in signals:
            self.plot_data(name, plot_phases=plot_phases)
            plot_phases = False
        plt.show()


if __name__ == "__main__":
    # Parse arguments
    args = arguments_parser()
    # Parse the data
    logging.info("Read: "+ args.txt_file+"\n")

    plotter = Plotter(args.txt_file)
    plotter.plot(args.signals)
