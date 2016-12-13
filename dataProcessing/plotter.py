"""
Script to plot data
"""
import logging

import pandas as pd
import matplotlib.pyplot as plt

from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment

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
        if input_file is None:
            self.data = pd.DataFrame()
            self.units = {}
        else:
            self.data, self.units = txt_parser(input_file, get_units=True)
            self.phases = segment(self.data)
        self.segments_color = {'climb': "r", 'cruise': "b",
                               'landing': 'm',
                               'descent': 'g', 'hold': "c",
                               'landing': 'm',
                               'otg': 'y', 'take_off': 'k'}



    def plot_data(self, signal1, signal2='Time'):
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
        plt.xlabel("{} [{}]".format(signal1, self.units.get(signal1, "")))
        plt.ylabel("{} [{}]".format(signal2, self.units.get(signal2, "")))
        # Add vertical bars to show different phases
        _, ymax = plt.ylim()
        for segment_name, segments in self.phases.items():
            # If not segments skip this phase
            if len(segments) == 0:
                continue
            segment_color = self.segments_color.get(segment_name, 'k')
            for start, end in segments:
                plt.axvline(x=start, color=segment_color, linestyle="dashed")
                plt.text(start, ymax, segment_name, verticalalignment="top",
                         color=segment_color, rotation=90)
                plt.axvline(x=end, color=segment_color, linestyle="dotted")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)


    def set_data(self, data, units=False):
        "Set data of the plotter"
        self.data = data
        self.phases = segment(data)
        if units:
            self.units = units


    def plot(self, signals):
        """
        Plot a list of signals

        :param signals: list
            List of signal name
        """
        for name in signals:
            self.plot_data(name)
        plt.show()


if __name__ == "__main__":
    # Parse arguments
    args = arguments_parser()
    # Parse the data
    logging.info("Read: "+ args.txt_file+"\n")

    plotter = Plotter(args.txt_file)
    plotter.plot(args.signals)
