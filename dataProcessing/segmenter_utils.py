"""
Utilst function for segmenter
"""

import numpy as np


def cut(time_list):
    """
        Create a list of tuples (time start,time end) from a list of discontinuous time values
    """
    if not time_list:
        return []

    # Check if there are jumps or not
    jumps = []
    for i in range(len(time_list)-2):
        if time_list[i + 1] != time_list[i] + 1:
            jumps.append((time_list[i],time_list[i+1]))

    if not jumps:
        # if time values are continuous, start time = first time, end time = last time
        return [(time_list[0],time_list[-1])]
    elif len(jumps)==1:
        # If there is one single jump, one segment before the jump, one segment after
        return [(time_list[0],jumps[0][0]),(jumps[0][1],time_list[-1])]

    # Compute dates
    dates = [ (time_list[0], jumps[0][0]) ]  # First segment
    for i in range(len(jumps)-1):
        # Intermediate segments
        dates.append((jumps[i][1], jumps[i+1][0]))
    dates.append((jumps[-1][1], time_list[-1])) # Last segment
    return dates


def hysteresis(x, th_lo, th_hi, init=False):
    hi = x >= th_hi
    lo_or_hi = (x <= th_lo) | hi
    ind = np.nonzero(lo_or_hi)[0]
    if not ind.size:
        return np.zeros_like(x, dtype=bool) | init
    cnt = np.cumsum(lo_or_hi)
    return np.where(cnt, hi[ind[cnt-1]], init)


def tuples_to_durations(dic):
    """
        Convert a dictionnary containing lists of tuples (t_start, t_end) as values into the same dictionnary with durations
        as values

        :param dic: dict
            Dictionnary with lists of tuples (t_start, t_end) as values
        :out dict
            Dictionnary with lists of durations as values
    """
    durations = {}
    for key, time_values in dic.items():
        durations[key] = sum(end-start for start, end in time_values)
    return durations


def get_weights(segments_dict, data):
    """
    Compute the duration of each segment divided by the duration of the flight

    :param segments_dict: dict
        Dictionnary containing flight segments, keys represent names of segments, values are lists of tuples (time start,time end)

    :param data: pd.DataFrame
        flight data

    :out: dict
        keys represent names of segments, values are float representing the time spent in this segment divided by the total duration of the flight
    """
    weights = {}
    total_duration = data.Time.iloc[-1] - data.Time.iloc[0]
    for segment in segments_dict.keys():
        weights[segment] = 0
        for time_values in segments_dict[segment]:
            weights[segment] += time_values[1] - time_values[0]
    return {k: v / total_duration for k, v in weights.items()}

