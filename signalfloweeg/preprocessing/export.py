# -*- coding: utf-8 -*-
"""
Module: export
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne

# Functions and classes
def save_Set(data: mne.io.Raw, save_directory: str, filename: str):
    """
    Save the preprocessed data as an EEGlab .set file.

    Args:
        data (mne.io.Raw): The preprocessed data to be saved.
        save_directory (str): The directory where the file will be saved.
        filename (str): The name of the file (without extension).

    Returns:
        None
    """
    filename = filename + "_preprocessed.set"
    mne.export.export_data(data, save_directory + filename, file_format='eeglab')
    pass

def save_Excel(data: mne.io.Raw, save_directory: str, filename: str):

    pass
# Add your module-specific functions and classes here
