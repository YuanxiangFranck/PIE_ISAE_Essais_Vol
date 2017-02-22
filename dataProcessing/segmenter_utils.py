"""
Utilst function for segmenter
"""

import numpy as np


def cut(times, dt=1):
    """
    Create a list of tuples (time start,time end) from a list of discontinuous time values

    :param times: pd.Series
        Series with time stamp of a phase
    :param [dt=1]: float
        difference between two time stamp
    :out: list of list
        List of couple of start, end time
    """
    time_list = times.values
    if not time_list.size:
        return []

    jumps = time_list[1:] != time_list[:-1]+dt
    nb_jumps = sum(jumps) # numbers of jumps

    dates = np.zeros((nb_jumps+1, 2))
    # Fist time value
    dates[0, 0] = time_list[0]
    # Last time value
    dates[-1, -1] = time_list[-1]
    # Add all other jumps
    dates[1:, 0] = time_list[1:][jumps]
    dates[:-1, 1] = time_list[:-1][jumps]
    return dates.tolist()


def hysteresis(x, th_lo, th_hi, init=False):
    """
    Compute hysteresis for take off, landing and descent

    :param x: pd.Series
        data to apply hysteresis on
    :param th_lo: float
        lower bound for the hysteresis
    :param th_hi: float
        high bound for the hysteresis
    :param [init=True]: bool
        initial value for the hysteresis

    :out: np.array
        array of boolean
    """
    hi = x >= th_hi
    lo_or_hi = (x <= th_lo) | hi
    ind = np.nonzero(lo_or_hi)[0]
    if not ind.size:
        return np.zeros_like(x, dtype=bool) | init
    cnt = np.cumsum(lo_or_hi)
    return np.where(cnt, hi[ind[cnt-1]], init).astype(bool)


def tuples_to_durations(dic):
    """
    Convert a dictionnary containing lists of tuples (t_start, t_end) as values into the same dictionnary with durations
    as values

    :param dic: dict
        Dictionnary with lists of tuples (t_start, t_end) as values
    :out : dict
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
    weights = tuples_to_durations(segments_dict)
    total_duration = data.Time.iloc[-1] - data.Time.iloc[0]
    return {k: v / total_duration for k, v in weights.items()}

