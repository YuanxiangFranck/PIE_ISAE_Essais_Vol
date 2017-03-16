# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 11:28:25 2017

@author: Matthieu

ILIAD

Symmetry

"""

# Standard imports
import time
import sys, os
sys.path.append(os.path.abspath('..'))
from dataProcessing.utils import logger

#Signal Data class import
from algorithms import SignalData

from algorithms.heatmap_symmetry import heatmap_symmetry

# Flight analysis functions import
from algorithms.Symmetry import (Symmetry_Channels_One_Flight, Symmetry_Lateral_One_Flight,
                                 Analyze_results, write_in_file, write_in_csv)

def asymmetry_detection(flight_data=None, error=0.01, save_csv=True, save_txt=True,
                        flight_name='undefined', out_dir='.', out_filename='auto',
                        conf=None, phase='undefined', heatmap=True, time_window='auto',
                        n_segments='auto', hclust=False, save_heatmap=True):
    """
    Runs the symmetry test for both lateral and channel symmetries : finds the
    signals which are expected to be equal but actually are different, gives the
    duration of anomaly of each pair and calculates the linear regression coefficients for
    regulation signals. It also can create an heatmap showing the relative anomaly
    duration for some time segmentation.

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

    - heatmap : a bool, choose to create or not the heatmap

    - time_window: int, length of the time window used to cut the flight into
    time segments, or 'auto' if n_segments is used instead

    - n_segments: int, number of time segments used to cut the flight, or 'auto' if time_window is used instead

    - hclust: boolean, apply hierarchical clustering to group similar signals

    - save_heatmap: boolean, save heatmap to a file

    """

    if not conf:
        logger.error("No configuration specified ! The conf argument must be "
                     "set to the current configuration object.")
        return

    if time_window == 'auto' and n_segments == 'auto':
        logger.error("The arguments time_window and n_segments cannot both be set to"
                     "'auto'. One of them must be specified.")
        return

    if time_window != 'auto' and n_segments != 'auto':
        logger.error("The arguments time_window and n_segments cannot both be "
                     "set to a value. One of them must be left to 'auto'.")
        return

    binary_names = conf["binary"]

    flight_phases = ["undefined", "otg", "take_off", "landing", "climb", "hold", "cruise", "descent"]

    if phase != "all":
        if phase not in flight_phases:

            logger.warning(
            "The input phase is unknown. The test is therefore apply on the whole flight.")
            phase = "undefined"

    if phase == "all":
        segments = flight_phases
    else:
        segments = [phase]

    for seg in segments:

        if seg != "undefined":
            flight_data.apply_flight_segmentation(seg)

        if len(flight_data.data) < 3:
            warning_message = "No file will be created for the phase "+seg+" because this phase is empty"
            logger.warning(warning_message)
        else:
            if seg == "undefined":
                print("\n Phase : Whole flight\n")
            else:
                print("\n Phase : "+seg+"\n")

            ###Run symetry algorithm
            ## With Channels
            result_channel = Symmetry_Channels_One_Flight(flight_data.data, error, binary_names)

            # Analyzes the results
            res_ch_analyzed = Analyze_results(result_channel, binary_names, str_type='channel')
            anomalies_channel_couples_names = res_ch_analyzed[0]
            anomalies_length_channel_couples = res_ch_analyzed[1]
            anomalies_channel_reg_coef = res_ch_analyzed[2]

            anomalies_relative_length_channel_couples = anomalies_length_channel_couples/len(flight_data.data)

            #..............................................
            ## With lateral Symmetry
            result_lat = Symmetry_Lateral_One_Flight(flight_data.data, error, binary_names)

            # Analyzes the results (disp number, and if booleans)
            res_lat_analyzed = Analyze_results(result_lat, binary_names, 'lat')
            anomalies_lat_couples_names = res_lat_analyzed[0]
            anomalies_length_lat_couples = res_lat_analyzed[1]
            anomalies_lat_reg_coef = res_lat_analyzed[2]

            anomalies_relative_length_lat_couples = anomalies_length_lat_couples/len(flight_data.data)


            # ecriture dans fichier
            if save_csv:
                out_path = out_dir
                if out_dir[-1] != '/':
                    out_path += '/'
                if out_filename == 'auto':
                    t = time.localtime()
                    out_path_channel = out_path + 'symmetry_anomaly_{}_channel_error_{}_phase_{}_{}{}{}-{}{}{}'\
                    .format(flight_name, error, seg, t[2], t[1], t[0],
                            t[3], t[4], t[5])
                    out_path_lat = out_path + 'symmetry_anomaly_{}_lateral_error_{}_phase_{}_{}{}{}-{}{}{}'\
                    .format(flight_name, error, seg, t[2], t[1], t[0],
                            t[3], t[4], t[5])
                else:
                    out_path_channel = out_path + out_filename + '_channel.csv'
                    out_path_lat = out_path + out_filename + '_lateral.csv'

                write_in_csv(out_path_channel, anomalies_channel_couples_names,
                             anomalies_relative_length_channel_couples,
                             anomalies_channel_reg_coef)
                write_in_csv(out_path_lat, anomalies_lat_couples_names,
                             anomalies_relative_length_lat_couples,
                             anomalies_lat_reg_coef)

            if save_txt:
                out_path = out_dir
                if out_dir[-1] != '/':
                    out_path += '/'
                if out_filename == 'auto':
                    t = time.localtime()
                    out_path_txt = out_path + 'symmetry_anomaly_{}_error_{}_phase_{}_{}{}{}-{}{}{}.txt'\
                    .format(flight_name, error, seg, t[2], t[1], t[0],
                            t[3], t[4], t[5])
                else:
                    out_path_txt += out_filename + '.txt'

                write_in_file(out_path_txt, flight_name, anomalies_channel_couples_names,
                              anomalies_relative_length_channel_couples,
                              anomalies_channel_reg_coef, error, 1, seg)
                write_in_file(out_path_txt, flight_name, anomalies_lat_couples_names,
                              anomalies_relative_length_lat_couples,
                              anomalies_lat_reg_coef, error, 0, seg)

        if seg != "undefined":
            flight_data.reset_data()

        # Create heatmap

        if heatmap:
            signals1_channel = [s[0] for s in anomalies_channel_couples_names]
            signals2_channel = [s[1] for s in anomalies_channel_couples_names]
            heatmap_symmetry(flight_data, error, time_window, n_segments,
                             hclust, save_heatmap, flight_name,
                             signals1_channel, signals2_channel, 'Channel',
                             out_dir, out_filename, False, 'pdf', conf)

            signals1_lat = [s[0] for s in anomalies_lat_couples_names]
            signals2_lat = [s[1] for s in anomalies_lat_couples_names]
            heatmap_symmetry(flight_data, error, time_window, n_segments,
                             hclust, save_heatmap, flight_name,
                             signals1_lat, signals2_lat, 'Lateral',
                             out_dir, out_filename, False, 'pdf', conf)



if __name__ == '__main__':
    from algorithms.flight_analysis_fun import load_flight
    from algorithms.signal_names import signal_names_bin

    flight_name = 'E190-E2_20001_0090_29867_54229_request.txt'


    path = '../data/'
    whole_flight = load_flight(path+flight_name)
    flight_data = SignalData.SignalData(whole_flight)


    conf = {"binary": signal_names_bin}
    asymmetry_detection(flight_data=flight_data, error=0.01, flight_name=flight_name, save_csv=True, save_txt=True,
                        out_dir='../analyse/1_vol_matthieu/resultats_symetrie/integration/', conf=conf)
