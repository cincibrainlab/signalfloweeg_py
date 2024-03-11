def spec_events_to_df(spec_events, filename, channel_no):
    """
    Convert the list of spectral events into a pandas DataFrame and add filename and channel number columns.

    Parameters
    ----------
    spec_events : list
        The list of spectral events, where each event is a dictionary.
    filename : str
        The name of the file from which the spectral events were extracted.
    channel_no : int
        The channel number corresponding to the spectral events.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the spectral events with filename and channel number columns.
    """
    # Flatten the list of lists of dictionaries to a single list of dictionaries
    flattened_events = [event for sublist in spec_events for event in sublist]
    
    # Convert the list of dictionaries to a DataFrame
    spec_events_df = pd.DataFrame(flattened_events)

    # Move filename and channel number to the first two columns
    spec_events_df.insert(0, 'Filename', filename)
    spec_events_df.insert(0, 'Channel_Number', channel_no)
    return spec_events_df
def read_eeglab_continuous(file_path):
    raw = mne.io.read_raw_eeglab(file_path, preload=True)
    return raw
def epoch_and_extract_eeg_data(raw, points_per_trial, channel_index=None, num_trials=None):
    """
    Reshape the EEG data array to the form (n_channels, n_times, n_trials) using MNE, with an optional channel index and an option for a fixed number of trials.

    Parameters
    ----------
    raw : instance of Raw
        The raw data.
    points_per_trial : int
        The number of time points per trial.
    channel_index : int, optional
        The index of the channel to extract. If None, all channels are returned.
    num_trials : int, optional
        The number of trials to extract. If None, all trials are returned.

    Returns
    -------
    epoch_data : ndarray
        The reshaped EEG data array.
    """
    # Create epochs from the raw data (n_epochs, n_sensors, n_times)
    epochs = mne.make_fixed_length_epochs(raw, duration=points_per_trial/raw.info['sfreq'], preload=True)
    # Get the data from epochs
    if channel_index is not None:
        epoch_data = epochs.get_data(picks=[channel_index]).squeeze()
        if num_trials is not None:
            epoch_data = epoch_data[:num_trials]
    else:
        epoch_data = epochs.get_data()
        # If a fixed number of trials is specified, select only that number of trials
        if num_trials is not None:
            epoch_data = epoch_data[:num_trials]
    # Ensure the data is reshaped to (n_channels, n_times, n_trials)
    if channel_index is not None:
        assert epoch_data.shape[1] == points_per_trial, "Points per trial do not match expected value."
    return epoch_data, epochs
def load_chirp_data(file_path, source=True, no_of_trials=80):
    """
    Load the continuous chirp .set file and extract the EEG data.
    """
    points_per_trial = 1626

    # Read the continuous .set file in the list
    raw = read_eeglab_continuous(file_path)

    # Extract EEG data from the raw data
    epoch_data, epochs = epoch_and_extract_eeg_data(raw, points_per_trial, channel_index=None, num_trials=no_of_trials)

    return epoch_data, epochs, raw
