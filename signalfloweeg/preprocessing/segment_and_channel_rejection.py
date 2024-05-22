import mne

def manual_segment_and_channel_rejection(data: mne.io.Raw):
    """
    Remove segments of data manually

    Parameters:
    - data (mne.io.Raw): Input data object.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # Function implementation goes here
    # data.load_data()
    # eog_events = mne.preprocessing.find_eog_events(data,ch_name=['E127','E126','E8','E25'])
    # onsets = eog_events[:, 0] / data.info["sfreq"] - 0.25
    # durations = [0.5] * len(eog_events)
    # descriptions = ["bad blink"] * len(eog_events)
    # blink_annot = mne.Annotations(
    #     onsets, durations, descriptions, orig_time=data.info["meas_date"]
    # )
    # data.set_annotations(blink_annot)
    
    # eeg_picks = mne.pick_types(data.info, meg=False, eeg=True)
    data.plot(n_channels=50, title="SignalFlowEGG", block=True)
    
    return data

#TODO
def ICA_rejection(data: mne.io.Raw):
    pass


def interpolate_bads(data: mne.io.Raw):
    """
    Interpolate bad channels
    Resets the bad channels to empty list after interpolation

    Parameters:
    - data (mne.io.Raw): Input data object.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # Function implementation goes here
    data.interpolate_bads(reset_bads=True)
    
    return data