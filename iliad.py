"""
ILIAD: Isae LIebherr Anomaly Detection
"""
import json
import logging
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment
from dataProcessing.summary import summary
from dataProcessing import plotter
from dataProcessing import utils
from algorithms.SignalData import SignalData
from algorithms.heatmap_visualization import heatmap


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
        self.path = path
        self.name = path.split("/")[-1][:-4]
        with open(config_path) as f_config:
            self.config = json.load(f_config)
        if verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        logging.basicConfig(format='%(levelname)s: %(message)s', level=level)

        # Parse data and compute signal_data
        logging.info("Start parsing: {}".format(path))
        self.signal_data = SignalData(txt_parser(path))

        # Compute flight segmentation
        logging.info("Start computing flight segmentation")
        self.phases, self.ports, self.ports_full_flight = segment(self.signal_data._raw_data)
        self._phases_idx = plotter.compute_phases_idx(self.phases, self.data.Time)
        self.signal_data.set_flight_segments(self.phases)

    @property
    def data(self):
        """
        return raw data from self.signal_data
        this function is built as a property, in order to use it as an attribute
        and avoid duplicate storage
        """
        return self.signal_data._raw_data

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
    # Export Reporting  #
    ##########################
    def export_reporting(self, out_dir="Resultats/"):
        "export html summary of the flight see summary.summary"
        utils.check_dir(out_dir)
        summary(self.path, data=self.data,
                phases_data=(self.phases, self.ports, self.ports_full_flight),
                out_dir=out_dir)

    def export_heatmap(self, out_dir='Resultats/', feature='off_regulation_crossings', signal_category='regulation'):
        "Export heatmap computation as pdf"
        # Create out dir if it don't exist
        utils.check_dir(out_dir)
        # Build heatmap
        heatmap(flight_data=self.signal_data, feature=feature,
                signal_category=signal_category, n_segments=50,
                flight_name=self.name, hclust=True, conf=self.config,
                out_dir=out_dir, show_plot=False,)


class Iliad_n_flight:
    "class to compare multiple flights"
    pass
