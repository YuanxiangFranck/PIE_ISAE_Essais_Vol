"""
ILIAD: Isae LIebherr Anomaly Detection
"""
import json
import logging
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment
from dataProcessing.summary import summary
from dataProcessing import plotter
from algorithms.SignalData import SignalData


class Iliad:
    """
    Class to group all the features

    Attributes:

    self.name (str): name of the flight
    self.config (dict): config of the algorithms
    self.data (DataFrame): flight_data
    self.phases (dict): phases of the plight
    self.ports (dict): port usage per segment
    self.ports_full_flight (dict) port usage on the whole flight

    Private attributes:

    self._phases_idx (dict) index (as bool) of the dataFrame for each segement
    """
    def __init__(self, path, config_path="dataProcessing/config.json", verbose=False):
        """
        Constuctor of the class
        """
        self.name = path.split("\\")[-1][:-3]
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
        self._phases_idx = plotter.compute_phases_idx(self.phases, self.data.Time)

    ######################
    # All plot functions #
    ######################
    def plot(self, *signals):
        "Use plotter to plot signals, see plotter.plot"
        plotter.plot(self.data, self._phases_idx, signals)

    def plot_phases(self):
        "Use plotter to plot phases, see plotter.plot"
        plotter.plot_phases(self.data.Time, self._phases_idx)

    def plot_segments_pie(self):
        "plot phases within a pie"
        plotter.plot_segments_pie(self.phases, self.data)

    def plot_ports_seg(self):
        "plot port usage on each segment on a pie chart, see plotter.plot_ports_seg"
        plotter.plot_ports_seg(self.ports)

    def plot_ports_sides(self):
        "plot port usage for each side of the plane, see plot_ports_sides"
        plotter.plot_ports_sides(self.ports_full_flight)

    def plot_ports(self):
        "plot port usage, see plot_ports"
        plotter.plot_ports(self.ports_full_flight, self.data)

    ##########################
    # Export HTML Reporting  #
    ##########################
    def export_reporting(self):
        "export html summary of the flight see summary.summary"
        summary(self.name, data=self.data,
                phases_data=(self.phases, self.ports, self.ports_full_flight))


class Iliad_n_flight:
    "class to compare multiple flights"
    pass
