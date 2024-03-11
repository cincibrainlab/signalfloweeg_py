# Execute another script and access its variables
import os, sys
import numpy as np
import mne
from matplotlib import pyplot as plt
import pandas as pd

# Add the path to the SpectralEvents package to the system path
sys.path.append('/Users/ernie/Documents/GitHub/SpectralEvents')
import spectralevents as se

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
def epoch_and_extract_eeg_data(epochs, points_per_trial, channel_index=None, num_trials=None):
    """
    Extract EEG data from epochs and optionally select data by channel index and number of trials.

    This function reshapes the EEG data array into the format (n_channels, n_times, n_trials) using MNE. 
    It allows for the selection of data from a specific channel and a specified number of trials.

    Parameters
    ----------
    epochs : instance of Epochs
        The epochs containing the EEG data.
    points_per_trial : int
        The number of time points for each trial.
    channel_index : int, optional
        The index of the specific channel to extract data from. If None, data from all channels are returned.
    num_trials : int, optional
        The specific number of trials to extract. If None, data from all trials are returned.

    Returns
    -------
    epoch_data : ndarray
        The EEG data array reshaped according to the specified parameters.
    epochs : instance of Epochs
        The epochs object passed to the function.
    """
    # Extract data from specified channel index, if provided
    if channel_index is not None:
        epoch_data = epochs.get_data(picks=[channel_index]).squeeze()
        # Limit the data to a specified number of trials, if provided
        if num_trials is not None:
            epoch_data = epoch_data[:num_trials]
    else:
        epoch_data = epochs.get_data()
        # Limit the data to a specified number of trials, if provided
        if num_trials is not None:
            epoch_data = epoch_data[:num_trials]
    # Verify the reshaped data matches the expected dimensions
    if channel_index is not None:
        assert epoch_data.shape[1] == points_per_trial, "Mismatch in the expected number of points per trial."
    return epoch_data, epochs

# ==============================================================================
# File Loading Stage
# ==============================================================================
# Brief on MNE file types: raw, epoched, evoked
# Raw: Continuous EEG data, unsegmented.
# Epoched: Data segmented into trials/events.
# Evoked: Averaged data over trials for specific conditions.

chirp_file = '/Users/ernie/Documents/ExampleData/Chirp/D0179_chirp-ST_postcomp_MN_EEG_Constr_2018.set'

# Extract the basename of the file for reporting and logging
file_basename = os.path.basename(chirp_file)
print(f"Processing file: {file_basename}")

# Read EEG data from the first .set file in the list
raw = mne.io.read_raw_eeglab(chirp_file, preload=True)

# Extract sampling frequency and channel names from the data
sf = raw.info['sfreq']  # Sampling frequency (Hz)
chans = raw.info['ch_names']  # List of EEG channel names

# Define EEG data parameters
no_of_channels = len(raw.info['ch_names'])  # Total number of EEG channels
points_per_trial = 1626  # Number of time points per trial
no_of_trials = 80  # Total number of trials

epochs = mne.make_fixed_length_epochs(raw, duration=points_per_trial/raw.info['sfreq'], preload=True)
epochs = epochs[:no_of_trials]

evoked = epochs.average()

# ==============================================================================

# ==============================================================================
# Spectral Events Analysis
# ==============================================================================

epoch_data, epochs = epoch_and_extract_eeg_data(epochs, points_per_trial, num_trials=80)

# Define the parameters for spectral event detection
freqs = np.arange(1, 60+1, 1)  # Frequency range in Hz
times = np.arange(points_per_trial) / sf  # Time points in seconds
event_band = [7.5, 12.5]  # Define the beta band frequency range in Hz
thresh_FOM = 4.0  # Set the factor-of-the-median threshold for event detection

# Extract EEG data for a specific channel
channel_no = 1  # Specify the channel number to analyze
chan_data = epoch_data[:, channel_no, :].squeeze()  # Squeeze to remove single-dimensional entries
print(f"Channel {channel_no} data shape: {chan_data.shape}")  # Log the shape of the channel data

# Perform time-frequency representation (TFR) analysis
tfrs = se.tfr(chan_data, freqs, sf)  # Calculate the TFR
fig = se.plot_avg_spectrogram(tfr=tfrs, times=times, freqs=freqs,
                              event_band=event_band)  # Plot the average spectrogram

# Detect spectral events within the specified frequency band and threshold
spec_events = se.find_events(tfr=tfrs, times=times, freqs=freqs,
                             event_band=event_band, threshold_FOM=thresh_FOM)  # Find spectral events

# Convert spectral events data to a DataFrame for easier handling
spec_events_df = spec_events_to_df(spec_events, os.path.basename(chirp_file), channel_no)  # Convert to DataFrame

# Save the spectral events data to a CSV file for further analysis
spec_events_df.to_csv('spectral_events.csv', index=False)  # Save DataFrame to CSV
