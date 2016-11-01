"""
Script to parse the data file
"""
import matplotlib.pyplot as plt
import pandas as pd
import logging

from parser import txt_parser


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


class Ploter:
    """
    Class to plot data from a txt file
    """
    def __init__(self, input_file=None):
        if input_file is None:
            self.data = pd.empty()
        else:
            self.data = txt_parser(input_file)
        self.nb_plots = 0

    def _plot_over_time(self, name):
        'add a figure to plt with the given options applied'
        if name not in self.data.columns:
            print(name+"  not in data")
            return
        self.nb_plots += 1
        plt.figure(self.nb_plots)
        out_message = 'PLOT '+name+' in figure '+str(self.nb_plots)
        x_data = self.data.Time
        y_data = self.data[name]
        label = name
        logging.info(out_message)
        plt.plot(x_data, y_data, label=label)
        plt.ylabel(name)
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)


    def set_data(self, data):
        self.data = data


    def plot(self, signals):
        for name in signals:
            self._plot_over_time(name)
        plt.show()


if __name__ == "__main__":
    # Parse arguments
    args = arguments_parser()
    # Parse the data
    logging.info("Read: "+ args.txt_file+"\n")

    ploter = Ploter(args.txt_file)
    ploter.plot(args.signals)
