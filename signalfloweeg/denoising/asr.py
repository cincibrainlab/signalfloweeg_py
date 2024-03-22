# Authors:  Ernest Pedapati (ernest.pedapati@cchmc.org)

def run_autoreject_raw( raw ):
    import autoreject
    epochs = epoch_vep_hbcd(raw)
    ar = autoreject.AutoReject(random_state=11,
                            n_jobs=20, verbose=True)
    ar.fit(epochs)  # fit on a few epochs to save time
    epochs_ar, reject_log = ar.transform(epochs, return_log=True)

    return epochs_ar, reject_log

def run_autoreject( epochs ):
    import autoreject
    ar = autoreject.AutoReject(n_interpolate=[1, 2, 3, 4], random_state=11,
                            n_jobs=30, verbose=True)
    ar.fit(epochs)  # fit on a few epochs to save time
    epochs_ar, reject_log = ar.transform(epochs, return_log=True)

    return epochs_ar, reject_log

def runStarCleaning( raw ):
    from meegkit import star 
    x_SC = raw.get_data().T   # Samples X Channels
    y, w, _ = star.star(x_SC, 2)
    raw_star = raw.copy()
    raw_star._data = y.T
    return raw_star

def run_asr( raw ):

    from meegkit.asr import ASR
    from meegkit.utils.matrix import sliding_window

    sfreq = int(raw.info['sfreq'])
    nchan = raw.info['nchan']

    raw_array = raw.get_data()

    # Train on a clean portion of data
    asr = ASR(method="euclid", cutoff=20)
    train_idx = np.arange(0 * sfreq, 20 * sfreq, dtype=int)
    _, sample_mask = asr.fit(raw_array[:, train_idx])

    # Apply filter using sliding (non-overlapping) windows
    X = sliding_window(raw_array, window=int(sfreq), step=int(sfreq))
    Y = np.zeros_like(X)
    for i in range(X.shape[1]):
        Y[:, i, :] = asr.transform(X[:, i, :])

    raw_array = X.reshape(nchan, -1)  # reshape to (n_chans, n_times)
    clean_array = Y.reshape(nchan, -1)

    raw_asr = raw.copy()
    raw_asr._data = clean_array
    return raw_asr

from meegkit.asr import ASR
from meegkit.utils.matrix import sliding_window
import numpy as np

def apply_asr(raw, method="euclid", cutoff=20, train_duration=20):
    """
    Apply Artifact Subspace Reconstruction (ASR) to EEG data.

    Parameters:
    - raw (mne.io.Raw): Raw EEG data object.
    - method (str): ASR method to use. Default is "euclid".
    - cutoff (float): Cutoff frequency for ASR in Hz. Default is 20 Hz.
    - train_duration (int): Duration of clean data used for training ASR in seconds. Default is 20 seconds.

    Returns:
    - raw_asr (mne.io.Raw): Raw EEG data object with ASR applied.
    """
    sfreq = int(raw.info['sfreq'])
    nchan = raw.info['nchan']

    raw_array = raw.get_data()

    # Train on a clean portion of data
    asr = ASR(method=method, cutoff=cutoff)
    train_idx = np.arange(0 * sfreq, train_duration * sfreq, dtype=int)
    _, sample_mask = asr.fit(raw_array[:, train_idx])

    # Apply filter using sliding (non-overlapping) windows
    X = sliding_window(raw_array, window=int(sfreq), step=int(sfreq))
    Y = np.zeros_like(X)
    for i in range(X.shape[1]):
        Y[:, i, :] = asr.transform(X[:, i, :])

    raw_array = X.reshape(nchan, -1)  # reshape to (n_chans, n_times)
    clean_array = Y.reshape(nchan, -1)

    raw_asr = raw.copy()
    raw_asr._data = clean_array

    return raw_asr

def run_zapline(raw):
    from meegkit import dss

    fline = int(60)
    data = raw.get_data().T # Convert mne data to numpy darray
    sfreq = raw.info['sfreq'] # Extract the sampling freq
    nchan = raw.info['nchan']

    #Apply MEEGkit toolbox function
    out, _ = dss.dss_line(data, fline, sfreq, nkeep=1) # fline (Line noise freq) = 50 Hz for Europe

    raw_zapline = raw.copy()
    raw_zapline._data = out.T
    return raw_zapline