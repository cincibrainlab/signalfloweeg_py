import mne

def manual_segment_rejection(data: mne.io.Raw):
    """
    Remove segments of data manually

    Parameters:
    - data (mne.io.Raw): Input data object.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # Function implementation goes here
    data.load_data()
    eog_events = mne.preprocessing.find_eog_events(data,ch_name=['E127','E126','E8','E25'], thresh= (max(data) - min(data)) / 8)
    onsets = eog_events[:, 0] / data.info["sfreq"] - 0.25
    durations = [0.5] * len(eog_events)
    descriptions = ["bad blink"] * len(eog_events)
    blink_annot = mne.Annotations(
        onsets, durations, descriptions, orig_time=data.info["meas_date"]
    )
    data.set_annotations(blink_annot)
    
    eeg_picks = mne.pick_types(data.info, meg=False, eeg=True)
    fig = data.plot(events=eog_events, order=eeg_picks, n_channels=50, title="SignalFlowEGG")
    fig.fake_keypress("a")  # Simulates user pressing 'a' on the keyboard.
    end = input("Press enter to continue\n")
    data.drop_bad()
    
    return data