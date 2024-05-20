# -*- coding: utf-8 -*-
"""
Package: signalfloweeg
Description: A Python package for EEG signal processing and analysis
"""
from . import preprocessing
from . import utils

__version__ = '0.1.3'  # Update this with your desired version number

def get_version():
    """
    Returns the version number of the signalfloweeg package.
    """
    return __version__