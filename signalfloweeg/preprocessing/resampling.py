# -*- coding: utf-8 -*-
"""
Module: resampling
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne

# Functions and classes
def resample(data:mne.io.Raw, sampling_freq:float = 500):
    raw_downsampled_poly = data.copy().resample(
        sfreq=sampling_freq,
        method="polyphase",
        verbose=False,
    )
    return raw_downsampled_poly

# Add your module-specific functions and classes here
