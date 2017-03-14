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
        self.phases, self.ports, self.ports_full_flight = segment(self.signal_data._raw_data, self.config)
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
        plotter.plot(self.data, self._phases_idx, self.config["phases_colors"],
                     signals)

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
                       n_segments=100,
                       hclust=False,
                       save=True,
                       out_filename='auto',
                       out_dir='./',
                       show_plot=True,
                       out_format='pdf',
                       annot=False,
                       robust=True):
        """
        Computes a feature on each time segment of a flight, and exports it as a heatmap visualization to a file. The result can be split across several files.

        :param flight_data: SignalData object
            Flight data

        :param feature: string
            The feature to represent on the heatmap

        :param signal_category: string
            The signal category represented on the heatmap. Should be one of the categories listed in the configuration file, or 'custom' to select signals manually

        :param signal list: list
            If signal_category is set to 'custom', list of strings containing selected signals

        :param time_window: int
            Length of the time window used to cut the flight into time segments, or 'auto' if n_segments is used instead

        :param n_segments: int
            Number of time segments used to cut the flight, or 'auto' if time_window is used instead

        :param hclust: boolean
            Apply hierarchical clustering to group similar signals

        :param save: boolean
            Save heatmap to a file

        :param flight_name: string
            Name of the flight

        :param out_dir: string
            Directory where the exported files will be saved

        :param out_filename: string
            Filename of the exported files, or 'auto' to generate an automatic filename

        :param show_plot: boolean
            Display figure in the python shell

        :param out_format: string
            'pdf' by default, or image format (i.e. 'png')

        :param annot: boolean
            Display values on the heatmap

        :param robust: boolean
            Use a robust color map. A robust color map gives a visually better result if the range of the values is large, by not taking into account extreme values in the color map.
            Be careful that the color axis does not represent the real value range with a robust color map ; you might want to use 'annot' = True to check the actual values.

        :param conf: dict
            Configuration
        """
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
        """
        Computes features on each time segment of a flight, performs OCSVM anomaly detection, and exports results to an anomaly heatmap and a csv report. The result can be split across several files.

        :param flight_data: SignalData object
            Flight data

        :param features: list
            List of strings containing features

        :param signal_categories: list
            List of strings containing the signal categories to process, or 'custom' to select signals manually. Signal categories are listed in the configuration file.

        :param signal list: list
            If signal_categories is set to 'custom', list of strings containing selected signals

        :param gamma: float
            gamma parameter of the OCSVM

        :param nu: float
            nu parameter of the OCSVM

        :param time_window: int
            Length of the time window used to cut the flight into time segments, or 'auto' if n_segments is used instead

        :param n_segments: int
            Number of time segments used to cut the flight, or 'auto' if time_window is used instead

        :param hclust: boolean
            Apply hierarchical clustering to group similar signals

        :param save: boolean
            Save heatmap and report to a file

        :param flight_name: string
            Name of the flight

        :param out_dir: string
            Directory where the exported files will be saved

        :param out_filename: string
            Filename of the exported files, or 'auto' to generate an automatic filename

        :param show_plot: boolean
            Display figure in the python shell

        :param out_format: string
            Output format of the anomaly heatmap. 'pdf' by default, or image format (i.e. 'png')

        :param conf: dict
            Configuration
        """
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
        """
        Computes features on each time segment of a flight, and exports a 2-dimensional PCA visualization to a file.

        :param flight_data: SignalData object
            Flight data

        :param features: list
            List of strings containing features

        :param signal_categories: list
            List of strings containing the signal categories to process, or 'custom' to select signals manually. Signal categories are listed in the configuration file.

        :param signal list: list
            If signal_categories is set to 'custom', list of strings containing selected signals

        :param time_window: int
            Length of the time window used to cut the flight into time segments, or 'auto' if n_segments is used instead

        :param n_segments: int
            Number of time segments used to cut the flight, or 'auto' if time_window is used instead

        :param hclust: boolean
            Apply hierarchical clustering to group similar signals

        :param save: boolean
            Save heatmap and report to a file

        :param flight_name: string
            Name of the flight

        :param out_dir: string
            Directory where the exported files will be saved

        :param out_filename: string
            Filename of the exported files, or 'auto' to generate an automatic filename

        :param show_plot: boolean
            Display figure in the python shell

        :param out_format: string
            image format ('png' by default)

        :param conf: dict
            Configuration
        """
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
                                   out_filename='auto',
                                   phase='undefined'):
        """
        Runs the symmetry test for both lateral and channel symmetries : finds the
        signals which are expected to be equal but actually are different, gives the
        duration of anomaly of each pair and calculates the linear regression coefficients for
        regulation signals.

        Inputs :

        - flight_data : must be an instance of SignalData. Contains all the data
        for the flight to analyse.

        - error : relative error used to compare a pair of continuous signals and
        detect anomalies. Is set to 0.01 (1%) by default.

        - save_csv : boolean for saving the results in two .csv files (1 for channel
        and 1 for lateral dissymmetry)

        - save_txt : boolean for saving the results into one .txt file (to open with
        bloc note for better visualisation)

        - flight_name : a string, contains the name of the flight.

        - out_dir : a string that indicates the relative output directory, in case
        of saving results

        - out_filename : name of the .txt saving file name, and part of the
        two .csv saving file names. If not defined or 'auto', then the format will be
        [symmetry_anomaly_{flight_name}_error_{error}_{time indications}.txt]

        - conf : used for configuration (it needs to contain the list of boolean signals)

        - phase : a string, allows to focus on one phase of the flight, among :
        "otg","take_off","landing","climb","hold","cruise","descent"
        set to "undefined" to run for the whole flight without phase consideration
        set to "all" to run for every phase, including the whole flight

        """
        asymmetry_detection(flight_data=self.signal_data, error=error, save_csv=save_csv,
                            out_filename=out_filename, flight_name=self.name,
                            out_dir=out_dir, save_txt=save_txt, conf=self.config,
                            phase = phase)


class Iliad_n_flight:
    "class to compare multiple flights"
    pass
