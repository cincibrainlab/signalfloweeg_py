# -*- coding: utf-8 -*-
"""
Module: io
Description: Module for handling input/output of data 
"""

from .import_eeg import *
from .validate_input import *

__all__ = ['validate_mne_type', 'load_eeg', 'get_num_epochs', 'get_amplitude_statistics']
