# -*- coding: utf-8 -*-
"""
Module: import_eeg
Description: Module for importing EEG data
"""

# Imports
import numpy as np
import mne

import mne

import os
import mne


def load_eeg_data(filename, file_ext=None):
    """
    Load EEG data from a file and return an MNE data object.

    Parameters:
    - filename (str): The name of the EEG file (without extension).
    - file_ext (str, optional): The file extension. If not provided, the function will try to autodetect the extension.

    Returns:
    - mne.io.BaseRaw, mne.Epochs, or mne.Evoked: The loaded EEG data as an MNE object.

    Supported file formats:
    - .edf, .bdf, .gdf, .vhdr, .fif, .fif.gz: Raw EEG data
    - -epo.fif, -epo.fif.gz: Epoched EEG data
    - -ave.fif, -ave.fif.gz: Evoked EEG data
    - .set, .set.zip: EEGLAB data
    """
    # Define the supported file extensions and their corresponding MNE reader functions
    readers = {
        ".edf": mne.io.read_raw_edf,
        ".bdf": mne.io.read_raw_bdf,
        ".gdf": mne.io.read_raw_gdf,
        ".vhdr": mne.io.read_raw_brainvision,
        ".fif": mne.io.read_raw_fif,
        ".fif.gz": mne.io.read_raw_fif,
        "-epo.fif": mne.read_epochs,
        "-epo.fif.gz": mne.read_epochs,
        "-ave.fif": mne.read_evokeds,
        "-ave.fif.gz": mne.read_evokeds,
        ".set": mne.io.read_raw_eeglab,
        ".set.zip": mne.io.read_raw_eeglab,
    }

    if file_ext is None:
        # Autodetect the file extension
        for ext in readers.keys():
            if os.path.exists(filename + ext):
                file_ext = ext
                break
        else:
            raise ValueError(f"No supported EEG file found for: {filename}")
    elif file_ext not in readers:
        raise ValueError(f"Unsupported file extension: {file_ext}")

    # Load the EEG data using the corresponding reader function
    reader_func = readers[file_ext]
    eeg_data = reader_func(filename + file_ext, preload=True)

    try:
        eeg_data = reader_func(filename + file_ext, preload=True)
    except ValueError as e:
        if file_ext in [".set", ".set.zip"] and "does not contain raw data" in str(e):
            # Attempt to load epoched data from EEGLAB .set file
            eeg_data = mne.io.read_epochs_eeglab(filename + file_ext)
        else:
            raise e

    return eeg_data
