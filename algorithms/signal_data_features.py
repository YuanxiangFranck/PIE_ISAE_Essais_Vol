"""
Script with all function to apply to the SignalData aggregate
"""

import numpy as np
from scipy.fftpack import dct

get_mean = np.mean
get_var = np.var
get_std = np.std
get_max = np.max
get_min = np.min
get_amplitude = lambda x: np.max(x) - np.min(x)
get_covariance = np.cov
# Count number of transition in binary signal
get_nb_transitions = lambda x: np.sum(x[1:] != x[:-1])

def get_fft(x, n_fft):
    """
    Renvoie les parties réelles et imaginaires des
    n_fft plus grands coefficients de Fourier
    """
    # Compute FFT coefficients (complex)
    coeffs = np.fft.rfft(x)
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
    coeffs = dct(x)
    # Sort according to absolute value
    coeffs_sorted = coeffs.ravel()[np.argsort(-np.abs(coeffs)).ravel()] \
    .reshape(coeffs.shape)
    # n_fft largest coefficients
    n_coeffs = coeffs_sorted[:,:n_dct]
    # Return the coefficients
    return n_coeffs
