# -*- coding: utf-8 -*-
"""
Détection de vols anormaux
"""

#%%
import sys,os
from time import time as tt;
from sklearn.decomposition import PCA

from dataProcessing.parser import txt_parser
from algorithms.SignalData import SignalData
import matplotlib.pyplot as plt


#%%
def init_data():
    """
    Load all flights and extract features
    """

def compute_data(flight_names, flights_data, segment_to_study,
                 needed_columns=None, needed_features=None, use_features=False):
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
            print("\n",name, ' already parsed')
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
            sigData.extractFeatures(needed_features)
        else:
            sigData.useWholeTimeseries()
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
    colors = ["b", "r", "y", "g", "m", 'c']
    # All all available scatter plot
    for i, f in enumerate(flights):
        if f is None: continue;
        ax.scatter(f[:, 0], f[:, 1], c=colors[i], label=flight_names[i])
    # Plot all scatter point
    title = "segment_{}_features_{}".format(segment_to_study, use_features)
    plt.legend(title=title, bbox_to_anchor=(0., 1.02, 1., 0.102),
               loc=3, borderaxespad=0)
    # Adjust the legend
    plt.tight_layout()
    fig.subplots_adjust(top=0.7)
    # Show or save the figure
    if plot_fig:
        plt.show()
    else:
        plt.savefig(title)


if __name__ == "__main__":
    usefeature = False
    # Matrix containing each flight's features in a row
    features = ['mean', 'min', 'max']
    cols = ['WOW_FBK_AMSC1_CHA', 'ADSP1 Pressure Altitude (feet)',
            'ADSP1 Altitude Rate (ft/min)',
            'ADSP1 Calibrated Airspeed (knots)']

    all_computed_data = {}
    signals_data = []
    dir_path = "../data/"
    file_names = os.listdir(dir_path)
    paths = [dir_path+ f for f in file_names]
    segments = ['climb', 'cruise', 'landing', 'descent', 'hold',
                'landing', 'otg', 'take_off']
    for i, segment in enumerate(segments):
        print("\n"*2, "="*10, "\n")
        print("Segment to study: ", segment)
        print("="*10, "\n")
        # compute scatter point
        computed_data = compute_data(paths, signals_data, segment,
                                     needed_columns=cols,
                                     needed_features=features,
                                     use_features=usefeature)
        # computed scatter points plots and save it
        plot(computed_data, file_names, segment, usefeature,
             figure=i+1, plot_fig=False)
        all_computed_data[segment] = computed_data[:]
    # Display all plots
    plt.show()