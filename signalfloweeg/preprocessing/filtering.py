# -*- coding: utf-8 -*-
"""
Module: filtering
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne

def bandpass_filter(data: mne.io.Raw, low_freq: float = 2, high_freq: float = 50):
    """
    Filter the input data using a bandpass filter.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - low_freq (float): Lower frequency bound of the bandpass filter.
    - high_freq (float): Upper frequency bound of the bandpass filter.

    Returns:
    - mne.io.Raw: Filtered data object.
    """
    # Function implementation goes here
    data.load_data()
    data.filter(l_freq=low_freq,h_freq=high_freq)
    return data

def highpass_filter(data: mne.io.Raw, low_freq: float = 2):
    """ 
    Filter the input data using a bandpass filter.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - low_freq (float): Lower frequency bound of the bandpass filter.

    Returns:
    - mne.io.Raw: Filtered data object.
    """
    # Function implementation goes here
    data.load_data()
    data.filter(l_freq=low_freq, h_freq=None)
    return data

def lowpass_filter(data: mne.io.Raw, high_freq: float = 50):
    """
    Filter the input data using a bandpass filter.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - high_freq (float): Upper frequency bound of the bandpass filter.

    Returns:
    - mne.io.Raw: Filtered data object.
    """
    # Function implementation goes here
    data.load_data()
    data.filter(l_freq=None, h_freq=high_freq)
    return data

def notch_filter(data: mne.io.Raw, freq: float = 60, notch_width: float = 5):
    """
    Filter the input data using a notch filter.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - freq (float): Frequency to filter out.
    - notch_width (float): Width of the notch filter.

    Returns:
    - mne.io.Raw: Filtered data object.
    """
    # Function implementation goes here
    data.load_data()
    data.notch_filter(freqs= freq, notch_widths= notch_width)
    return data


