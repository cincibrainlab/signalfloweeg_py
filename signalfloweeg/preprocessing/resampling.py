# -*- coding: utf-8 -*-
"""
Module: resampling
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne

# Functions and classes
def resample(data: mne.io.Raw, sampling_freq: float = 500):
    """
    Resamples the given data to the specified sampling frequency.

    Parameters:
        data (mne.io.Raw): The input data to be resampled.
        sampling_freq (float): The desired sampling frequency (in Hz) for the resampled data. Default is 500 Hz.

    Returns:
        mne.io.Raw: The resampled data.

    """
    data.resample(
        sfreq=sampling_freq,
        method="polyphase",
        verbose=False,
    )
    return data

# Add your module-specific functions and classes here
