"""
Script to parse the data file
"""
import logging

import pandas as pd
import matplotlib.pyplot as plt

from dataProcessing.parser import txt_parser


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
        else:
            self.data = txt_parser(input_file)
        self.nb_plots = 0


    def plot_data(self, signal1, signal2='Time'):
        "Plot one data over a second data in a scatter cloud"
        # Check if each signal are in data
        if signal1 not in self.data.columns:
            print(signal1+"  not in data")
            return
        if signal2 not in self.data.columns:
            print(signal2+"  not in data")
            return
        if signal2 == "Time":
            signal2, signal1 = signal1, signal2
        # Increment figure number
        self.nb_plots += 1
        plt.plot(self.data[signal1], self.data[signal2],
                 label=signal1+" / "+signal2)
        plt.ylabel(signal1)
        plt.ylabel(signal2)
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)





    def set_data(self, data):
        self.data = data


    def plot(self, signals):
        for name in signals:
            self._plot_data(name)
        plt.show()


if __name__ == "__main__":
    # Parse arguments
    args = arguments_parser()
    # Parse the data
    logging.info("Read: "+ args.txt_file+"\n")

    ploter = Plotter(args.txt_file)
    ploter.plot(args.signals)
