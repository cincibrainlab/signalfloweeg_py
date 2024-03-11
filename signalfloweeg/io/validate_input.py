# -*- coding: utf-8 -*-
"""
Module: validate_input
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne

import mne

def validate_mne_type(input_data, allowed_types, func_name):
    # Check if input_data is of the allowed MNE type
    # If not, raise a TypeError
    if not isinstance(input_data, allowed_types):
        raise TypeError(f"Input to {func_name} must be one of the following types: {', '.join(t.__name__ for t in allowed_types)}")
    else:
        return input_data

# Example Use:
# from signalflow.validation import validate_mne_type
# def my_function(data):
#    valid_data = validate_mne_type(data, (mne.io.Raw, mne.Epochs, mne.Evoked), "my_function")
