"""
ILIAD: Isae LIebherr Anomaly Detection
"""
import logging
import json
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment
from dataProcessing.summary import summary
from dataProcessing import plotter
from dataProcessing import utils
from dataProcessing.utils import logger
from algorithms.SignalData import SignalData
from algorithms.heatmap_visualization import heatmap
from algorithms.ocsvm_anomaly_detection import ocsvm_detection
from algorithms.pca_visualization import pca_visualization
from algorithms.symmetry_anomaly_detection import asymmetry_detection


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
        # Set logger (iliad)
        if verbose:
            level = logging.INFO
        else:
            level = logging.WARNING
        # Create logger
        logger.setLevel(level)

        # Parse data and compute signal_data
        logger.info("Start parsing: {}".format(path))
        self.signal_data = SignalData(txt_parser(path, target_names=self.config["target"]))

        # Compute flight segmentation
        logger.info("Start computing flight segmentation")
        self.phases, self.ports, self.ports_full_flight = segment(self.signal_data._raw_data)
        self._phases_idx = plotter.compute_phases_idx(self.phases, self.data.Time)
        self.signal_data.set_flight_segments(self.phases, self.ports_full_flight)

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
        plotter.plot_phases(self.data.Time, self._phases_idx,
                            self.config["phases_colors"])

    def plot_segments_pie(self):
        "plot phases within a pie"
        plotter.plot_segments_pie(self.phases, self.data,
                            self.config["phases_colors"])

    def plot_ports_seg(self):
        "plot port usage on each segment on a pie chart, see plotter.plot_ports_seg"
        plotter.plot_ports_seg(self.ports, self.config["ports_colors"])

    def plot_ports_sides(self):
        "plot port usage for each side of the plane, see plot_ports_sides"
        plotter.plot_ports_sides(self.ports_full_flight, self.config["ports_colors"])

    def plot_ports(self):
        "plot port usage, see plot_ports"
        plotter.plot_ports(self.ports_full_flight, self.data, self.config["ports_colors"])

    ##########################
    # Export Reporting  #
    ##########################
    def export_reporting(self, out_dir="Resultats/"):
        "export html summary of the flight see summary.summary"
        utils.check_dir(out_dir)
        summary(self.path, data=self.data,
                phases_data=(self.phases, self.ports, self.ports_full_flight),
                out_dir=out_dir)

    def export_heatmap(self, feature='percent_time_off_regulation',
                       signal_category='regulation',
                       signal_list=None,
                       time_window='auto',
                       n_segments='auto',
                       hclust=False,
                       save=True,
                       out_filename='auto',
                       out_dir='Resultats/',
                       show_plot=True,
                       out_format='pdf',
                       annot=False,
                       robust=True):
        "Export heatmap computation as pdf"
        # Create out dir if it don't exist
        utils.check_dir(out_dir)
        # Build heatmap
        heatmap(flight_data=self.signal_data, conf=self.config,flight_name=self.name,
                feature=feature, save=save, signal_category=signal_category,
                n_segments=n_segments, hclust=hclust, out_dir=out_dir,
                show_plot=show_plot, signal_list=signal_list,
                time_window=time_window, out_filename=out_filename,
                out_format=out_format, annot=annot, robust=robust)

    def export_ocsvm(self,
                     features=['mean', 'std', 'amplitude'],
                     signal_categories=['regulation','endogene'],
                     signal_list=None,
                     gamma=0.1,
                     nu=0.3,
                     time_window='auto',
                     n_segments=100,
                     hclust=False,
                     save=True,
                     report=True,
                     out_dir='.',
                     out_filename='auto',
                     show_plot=True,
                     out_format='pdf'):
        "TODO DOCSTRING"
        ocsvm_detection(flight_data=self.signal_data, features=features,
                        signal_categories=signal_categories,
                        signal_list=signal_list, gamma=gamma, nu=nu,
                        time_window=time_window, n_segments=n_segments,
                        hclust=hclust, save=save, report=report,
                        flight_name=self.name, out_dir=out_dir,
                        out_filename=out_filename, show_plot=show_plot,
                        out_format=out_format, conf=self.config)

    def export_pca(self, features=['mean', 'std', 'amplitude'],
                   signal_categories=['regulation','endogene'],
                   signal_list=None,
                   time_window='auto',
                   n_segments=100,
                   save=True,
                   out_dir='.',
                   out_filename='auto',
                   show_plot=True,
                   out_format='png'):
        "TODO"
        pca_visualization(flight_data=self.signal_data, features=features,
                          signal_categories=signal_categories,
                          signal_list=signal_list, time_window=time_window,
                          n_segments=n_segments, save=save,
                          flight_name=self.name, out_dir=out_dir,
                          out_filename=out_filename, show_plot=show_plot,
                          out_format=out_format, conf=self.config)

    def export_asymmetry_detection(self, error=0.01,
                                   save_csv=True,
                                   save_txt=True,
                                   out_dir='.',
                                   out_filename='auto'):
        "TODO!!!!"
        asymmetry_detection(flight_data=self.signal_data, error=error, save_csv=save_csv,
                            out_filename=out_filename, flight_name=self.name,
                            out_dir=out_dir, save_txt=save_txt, conf=self.config)


class Iliad_n_flight:
    "class to compare multiple flights"
    pass
