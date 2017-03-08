# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 11:28:25 2017

@author: Matthieu

ILIAD

Symmetry

TO DO:
    * tests
    * regler les pb de paths
    * pb il trouve + d'erreurs que dans symmetry_analysis ?
    * adds-on
"""

# Standard imports
import time
import logging

#Signal Data class import
from algorithms import SignalData

# Flight analysis functions import
from algorithms.Symmetry import (Symmetry_Channels_One_Flight, Symmetry_Lateral_One_Flight,
                                 Analyze_results, write_in_file, write_in_csv)

def asymmetry_detection(flight_data=None, error=0.01, save_csv=True, save_txt=True,
                        flight_name='undefined', out_dir='.', out_filename='auto',
                        conf=None):
    """
    Runs the symmetry test for both lateral and channels symmetries : finds the
    signals which are expected equal but actually are different, gives the duration
    of anomaly of each pair and calculates the linear regression coefficients.

    Inputs :

    - flight_data : must be an instance of SignalData. Contains all the data
    for the flight to analyse

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

    - conf : used for configuration

    -
    """
    # Handle arguments
    if not isinstance(flight_data, SignalData.SignalData):
        logging.warning(
        """The data argument must be a SignalData object containing the flight
        data.""")
        return

    ###Run symetry algorithm
    ## With Channels
    binary_names = conf["binary"]
    result_channel = Symmetry_Channels_One_Flight(flight_data.data, error, binary_names)

    # Analyzes the results
    res_ch_analyzed = Analyze_results(result_channel, 'channel', binary_names)
    anomalies_channel_couples_names = res_ch_analyzed[0]
    anomalies_length_channel_couples = res_ch_analyzed[1]
    anomalies_channel_reg_coef = res_ch_analyzed[2]

    anomalies_relative_length_channel_couples = anomalies_length_channel_couples/len(flight_data.data)

    #..............................................
    ## With lateral Symmetry
    result_lat = Symmetry_Lateral_One_Flight(flight_data.data, error)

    # Analyzes the results (disp number, and if booleans)
    res_lat_analyzed = Analyze_results(result_lat, 'lat', binary_names)
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
            out_path_channel = out_path + 'symmetry_anomaly_{}_channel_error_{}_{}{}{}-{}{}{}'\
            .format(flight_name, error, t[2], t[1], t[0],
                    t[3], t[4], t[5])
            out_path_lat = out_path + 'symmetry_anomaly_{}_lateral_error_{}_{}{}{}-{}{}{}'\
            .format(flight_name, error, t[2], t[1], t[0],
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
            out_path_txt = out_path + 'symmetry_anomaly_{}_error_{}_{}{}{}-{}{}{}.txt'\
            .format(flight_name, error, t[2], t[1], t[0],
                    t[3], t[4], t[5])
        else:
            out_path_txt += out_filename + '.txt'

        write_in_file(out_path_txt, flight_name, anomalies_channel_couples_names,
                      anomalies_relative_length_channel_couples,
                      anomalies_channel_reg_coef,error, 1)
        write_in_file(out_path_txt, flight_name, anomalies_lat_couples_names,
                      anomalies_relative_length_lat_couples,
                      anomalies_lat_reg_coef,error, 0)


if __name__ == '__main__':
    from algorithms.flight_analysis_fun import load_flight
    from algorithms.signal_names import signal_names_bin

    flight_name = 'E190-E2_20001_0090_29867_54230_request.txt'


    path = '../data/'
    whole_flight = load_flight(path+flight_name)
    flight_data = SignalData.SignalData(whole_flight)


    conf = {"binary": signal_names_bin}
    asymmetry_detection(flight_data=flight_data, error=0.01, flight_name=flight_name, save_csv=True, save_txt=True,
            out_dir='./', conf=conf)
