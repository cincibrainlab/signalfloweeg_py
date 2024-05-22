# -*- coding: utf-8 -*-
"""
Module: rereferencing
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne

# Functions and classes
def rereference_average(data: mne.io.Raw) -> mne.io.Raw:
    """
    Re-references the EEG data to the average reference.

    Parameters:
    data (mne.io.Raw): The raw EEG data.

    Returns:
    mne.io.Raw: The re-referenced EEG data.
    """
    data.set_eeg_reference(ref_channels='average', copy=False, ch_type='eeg', verbose='debug')
    #projection?
    return data

# Add your module-specific functions and classes here
