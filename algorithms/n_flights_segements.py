# -*- coding: utf-8 -*-
"""
Détection de vols anormaux
"""
import os
from math import inf
from time import time as tt
from sklearn.decomposition import PCA

from dataProcessing.parser import txt_parser
from algorithms.SignalData import SignalData
import matplotlib.pyplot as plt


def compute_data(flight_names, flights_data, segment_to_study,
                 needed_columns=None, needed_features=None, use_features=False,
                 ravel_features=True):
    """
    loop over file and compute data
    :path: string

    """
    flights = []
    for nb_flight, name in enumerate(flight_names):
        t0 = tt()
        is_not_saved = nb_flight == len(flights_data)
        # No saved data -> parse it
        if is_not_saved:
            print("\nProcessing flight ", name)
            flight_data = txt_parser(name)
            # Extract features for each flight
            sigData = SignalData(flight_data, 100)
            flights_data.append(sigData)
        else:
            # Otherwise reset data is SignalData obj
            print("\n", name, ' already parsed')
            sigData = flights_data[nb_flight]
            sigData.reset_data()
        # Get data when flight is on selected segment
        sigData.apply_flight_segmentation(segment_to_study)
        # If no hold segment skip this flight
        if sigData.data.empty:
            print("skip flight...")
            flights.append(None)
            continue
        if needed_columns is not None:
            # Restrict columns to the interesting one
            sigData.data = sigData.data.loc[:, needed_columns]
        if needed_features is not None and use_features:
            sigData.extractFeatures(needed_features, ravel_features=ravel_features)
        else:
            sigData.useWholeTimeseries()
        # Remove nan
        sigData.X.dropna(inplace=True)
        # Normalize features
        sigData.normalizeFeatures()
        reduced_data = PCA(n_components=2).fit_transform(sigData.X)
        # Store data
        flights.append(reduced_data)
        print("processing done in", tt() - t0)
    return flights


def plot(flights, flight_names, segment_to_study, use_features,
         figure=1, plot_fig=True):
    "plot computed data"
    fig = plt.figure(figure)
    ax = fig.add_subplot(111)
    colors = ["b", "r", "y", "g", "m", 'c', "k"]
    # All all available scatter plot
    maxy, miny = -inf, inf
    maxx, minx = -inf, inf
    for nf, fl in enumerate(flights):
        if fl is None: continue;
        ax.scatter(fl[:, 0], fl[:, 1], c=colors[nf], label=flight_names[nf])
        maxx = max(maxx, fl[:, 0].max())
        minx = min(minx, fl[:, 0].min())
        maxy = max(maxy, fl[:, 1].max())
        miny = min(miny, fl[:, 1].min())
    # rescale
    plt.xlim((minx, maxx))
    plt.ylim((miny, maxy))
    # Adjust the legend
    title = "segment_{}_features_{}".format(segment_to_study, use_features)
    plt.legend(title=title, bbox_to_anchor=(0., 1.02, 1., 0.102),
               loc=3, borderaxespad=0)
    plt.tight_layout()
    fig.subplots_adjust(top=0.7)
    # Show or save the figure
    if plot_fig:
        plt.show()
    else:
        plt.savefig(title)


def init(cas):
    "Initialize different senario"
    if cas == 1:
        ## Cas 1: sans features, donnée brut
        usefeature = False
        features = ['mean', 'min', 'max', "covariance"]
        cols = ['WOW_FBK_AMSC1_CHA',
                'ADSP1 Pressure Altitude (feet)',
                'ADSP1 Altitude Rate (ft/min)',
                'ADSP1 Calibrated Airspeed (knots)']
        ravelfeatures = True
    elif cas == 2:
    ## Cas 2: sans features, donnée filtrée
        usefeature = False
        features = ['mean', 'min', 'max', "covariance"]
        cols = ['WOW_FBK_AMSC1_CHA',
                'ADSP1 Pressure Altitude (feet)',
                'alt_rate_signal',
                'delta_cas_signal']
        ravelfeatures = True
    elif cas == 3:
        ## Cas 3: avec features, donnée filtrée
        usefeature = True
        features = ['mean', 'min', 'max', "covariance"]
        cols = ['WOW_FBK_AMSC1_CHA',
                'ADSP1 Pressure Altitude (feet)',
                'alt_rate_signal',
                'delta_cas_signal']
        ravelfeatures = True
    elif cas == 4:
        ## avec features, donnée filtrée, unravel features
        usefeature = True
        features = ['mean', 'min', 'max', "covariance"]
        cols = ['WOW_FBK_AMSC1_CHA',
                'ADSP1 Pressure Altitude (feet)',
                'alt_rate_signal',
                'delta_cas_signal']
        ravelfeatures = True
    return usefeature, features, cols, ravelfeatures


if __name__ == "__main__":
    usefeature, features, cols, ravelfeatures = init(1)
    all_computed_data = {}
    signals_data = []
    dir_path = "../data/"
    file_names = os.listdir(dir_path)
    paths = [dir_path + f for f in file_names]
    segments = ['climb', 'cruise', 'landing', 'descent', 'hold',
                'landing', 'otg', 'take_off']
    for segment in segments:
        print("\n"*2, "="*10, "\n")
        print("Segment to study: ", segment)
        print("="*10, "\n")
        # compute scatter point
        computed_data = compute_data(paths, signals_data, segment,
                                     needed_columns=cols,
                                     needed_features=features,
                                     use_features=usefeature,
                                     ravel_features=ravelfeatures)
        # computed scatter points plots and save it
        fig_name = "segment_"+segment+"_features_"+("_".join(features))
        plot(computed_data, file_names, segment, usefeature,
             figure=fig_name, plot_fig=False)
        all_computed_data[segment] = computed_data[:]
    # Display all plots
    plt.show()
