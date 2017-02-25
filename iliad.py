"""
ILIAD: Isae LIebherr Anomaly Detection
"""
import json
import logging
from dataProcessing.parser import txt_parser, compute_phases_idx
from dataProcessing.segmenter import segment
from dataProcessing import plotter
from algorithms.SignalData import SignalData


class Iliad:
    """
    Class to group all the features

    Attributes:

    self.config: dict
    self.data (DataFrame): flight_data
    self.phases (dict): phases of the plight
    self.ports (dict): port usage per segment
    self.ports_full_flight (dict) port usage on the whole flight

    Private attributes:

    self._phases_idx (dict) index (as bool) of the dataFrame for each segement
    """
    def __init__(self, path, config_path="dataProcessing/config.json", verbose=False):
        with open(config_path) as f_config:
            self.config = json.load(f_config)
        if verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.basicConfig(format='%(levelname)s: %(message)s', level=level)

        logging.info("Start parsing: {}".format(path))
        self.data = txt_parser(path)
        logging.info("Input file parsed.")
        self.phases, self.ports, self.ports_full_flight = segment(self.data)
        self._phases_idx = compute_phases_idx(self.phases, self.data.Time)

    def plot(self, *signals):
        "Use plotter to plot signals, see plotter.plot"
        plotter.plot(self.data, self._phases_idx, signals)

    def plot_phases(self):
        "Use plotter to plot phases, see plotter.plot"
        plotter.plot_phases(self.data.Time, self._phases_idx)

class Iliad_n_flight:
    "class to compare multiple flights"
    pass
