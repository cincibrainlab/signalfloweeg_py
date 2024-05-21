# -*- coding: utf-8 -*-
"""
Module: area
Description: [Insert module description here]
"""

# Imports
import numpy as np
import mne
from fooof import FOOOF
from fooof.sim.gen import gen_aperiodic

# Functions and classes
def riemanArea(fm):
    aperiodic = gen_aperiodic(fm.freqs, fm._robust_ap_fit(fm.freqs, fm.power_spectrum))
    frequencies = fm.freqs
    periodic = fm.fooofed_spectrum_
    riemanArea = np.zeros(len(frequencies))
    stepSize = frequencies[1] - frequencies[0]
    for i in range(len(frequencies)-1):
        riemanArea[i] = stepSize * ((periodic[i] - aperiodic[i]) + (periodic[i+1] - aperiodic[i+1]))/2

    return riemanArea

# Add your module-specific functions and classes here