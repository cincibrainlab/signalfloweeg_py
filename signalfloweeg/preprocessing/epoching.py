# -*- coding: utf-8 -*-
"""
Module: epoching
Description: This module provides functions for epoching EEG data.
"""

# Imports
import numpy as np
import mne

# Functions and classes
def epoch_time(raw:mne.io.Raw, epoch_length:float):
    """
    Epochs the given raw EEG data into fixed-length epochs.

    Parameters:
    raw (mne.io.Raw): The raw EEG data.
    epoch_length (float): The duration of each epoch in seconds.

    Returns:
    epochs (mne.Epochs): The epoch object containing the segmented data.
    """
    epochs = mne.make_fixed_length_epochs(raw, duration=epoch_length, preload=False)
    return epochs

# Add your module-specific functions and classes here
