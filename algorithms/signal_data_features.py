"""
Script with all function to apply to the SignalData aggregate
"""

import numpy as np
from scipy.fftpack import dct

get_mean = lambda x: np.mean(x, axis=0)
get_var = lambda x: np.var(x, axis=0)
get_std = lambda x: np.std(x, axis=0)
get_max = lambda x: np.max(x, axis=0)
get_min = lambda x: np.min(x, axis=0)
get_amplitude = lambda x: np.max(x, axis=0) - np.min(x, axis=0)
get_covariance = lambda x: np.cov(x, axis=0)
# Count number of transition in binary signal
get_nb_transitions = lambda x: np.sum(x[1:, :] != x[:-1, :], axis=0)

# Detect if value is greater than specified threshold
def get_time_over_threshold(x, val):
    """
    Renvoie le nombre de pas de temps durant lesquels
    abs(x) est supérieur à un certain seuil val
    """
    return np.sum(np.abs(x) > val)

def get_percent_time_over_threshold(x, val):
    """
    Renvoie la proportion de pas de temps durant lesquels
    abs(x) est supérieur à un certain seuil val
    """
    return np.mean(np.abs(x) > val)

def get_mean_crossings(x):
    """
    Renvoie le nombre de passages de la moyenne de x
    """
    mu = np.mean(x)
    prec = x.iloc[0] < mu
    count = 0
    for xi in x.iloc[1:]:
        if (xi < mu) != prec:
            count += 1
            prec = not(prec)
    return count

def get_fft(x, n_fft):
    """
    Renvoie les parties réelles et imaginaires des
    n_fft plus grands coefficients de Fourier
    """
    # Compute FFT coefficients (complex)
    coeffs = np.fft.rfft(x.transpose())
    # Sort according to absolute value
    coeffs_sorted = coeffs.ravel()[np.argsort(-np.abs(coeffs)).ravel()] \
    .reshape(coeffs.shape)
    # n_fft largest coefficients
    n_coeffs = coeffs_sorted[:,:n_fft]
    # Return real and imaginary parts
    return np.append(np.real(n_coeffs),np.imag(n_coeffs),axis=1)

def get_dct(x, n_dct):
    """
    Renvoie les n_dct plus grands coefficients de la transformée en 
    cosinus discrète 
    """
    # Compute FFT coefficients (complex)
    coeffs = dct(x.transpose())
    # Sort according to absolute value
    coeffs_sorted = coeffs.ravel()[np.argsort(-np.abs(coeffs)).ravel()] \
    .reshape(coeffs.shape)
    # n_fft largest coefficients
    n_coeffs = coeffs_sorted[:,:n_dct]
    # Return the coefficients
    return n_coeffs
