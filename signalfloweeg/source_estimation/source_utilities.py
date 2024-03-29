import mne
from mne.datasets import fetch_fsaverage
import os.path as op
from os import path, makedirs, dirname


# Load the fsaverage brain model for visualization
def load_fsaverage_brain():
    
    # bem: Boundary Element Model files for forward solution computation
    # label: Brain region of interest label files
    # mri: Structural MRI data of the fsaverage brain
    # mri.2mm: Structural MRI data resampled to 2mm resolution
    # scripts: Custom analysis scripts (preprocessing, source localization, etc.)
    # surf: Brain surface files (white matter, pial) for source localization and visualization
    
    fs_dir = fetch_fsaverage(verbose=True)
    subjects_dir = dirname(fs_dir)
    return fs_dir, subjects_dir

# Load the source space and BEM model
def load_source_bem_fwd(info, source_file, bem_file, trans, mindist=5.0, n_jobs=10):
    """
    Load the source space and BEM model for forward solution computation.

    Parameters:
    info (mne.Info): The measurement information.
    source_file (str): The file path to the source space.
    bem_file (str): The file path to the BEM model.
    trans (str): The transformation file.
    mindist (float, optional): The minimum distance from the source space to the inner skull surface. Defaults to 5.0.
    n_jobs (int, optional): The number of jobs to run in parallel. Defaults to 10.

    Returns:
    src (mne.SourceSpaces): The source space.
    bem (mne.bem.BEMSolution): The BEM model.
    fwd (mne.Forward): The forward solution.
    cov (mne.Covariance): The noise covariance matrix.
    inv (mne.minimum_norm.InverseOperator): The inverse operator.
    """
    # ------------------------------------------------------------------------------
    # Constructing Source Space File Path
    # ------------------------------------------------------------------------------
    src = mne.read_source_spaces(source_file)

    # ------------------------------------------------------------------------------
    # Constructing BEM File Path
    # ------------------------------------------------------------------------------
    bem = mne.read_bem_solution(bem_file)

    # ------------------------------------------------------------------------------
    # Forward Solution Creation
    # ------------------------------------------------------------------------------
    fwd = mne.make_forward_solution(info, trans=trans, src=src, bem=bem, eeg=True, mindist=mindist, n_jobs=n_jobs)
    
    # ------------------------------------------------------------------------------
    # Noise Covariance Matrix Computation
    # ------------------------------------------------------------------------------
    cov = mne.make_ad_hoc_cov(info)

    # ------------------------------------------------------------------------------
    # Inverse Operator Creation
    # ------------------------------------------------------------------------------
    inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, verbose=True)

    return src, bem, fwd, cov, inv
    # ------------------------------------------------------------------------------
    # Constructing Source Space File Path
    # ------------------------------------------------------------------------------
    src = mne.read_source_spaces(source_file)

    # ------------------------------------------------------------------------------
    # Constructing BEM File Path
    # ------------------------------------------------------------------------------
    bem = bem_file

    # ------------------------------------------------------------------------------
    # Forward Solution Creation
    # ------------------------------------------------------------------------------
    fwd = mne.make_forward_solution(info, trans=trans, src=src, bem=bem, eeg=True, mindist=mindist, n_jobs=n_jobs)
    
    # ------------------------------------------------------------------------------
    # Noise Covariance Matrix Computation
    # ------------------------------------------------------------------------------
    cov = mne.make_ad_hoc_cov(info)

    # ------------------------------------------------------------------------------
    # Inverse Operator Creation
    # ------------------------------------------------------------------------------
    inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, verbose=True)

    return src, bem, fwd, cov, inv

# Write the inverse operator to disk
def write_inverse_operator(raw, inv, output_dir):
    """
    Write the inverse operator to disk.

    Parameters:
    raw (mne.io.Raw): The raw EEG data.
    inv (mne.minimum_norm.InverseOperator): The inverse operator.
    output_dir (str): The directory to save the inverse operator file.
    """
    def extract_basename(raw):
        return path.splitext(path.basename(raw.filenames[0]))[0]

    makedirs(output_dir, exist_ok=True)
    inv_fname = path.join(output_dir, f"{extract_basename(raw)}-inv.fif")
    mne.minimum_norm.write_inverse_operator(inv_fname, inv, overwrite=True)

# Apply the inverse operator to the EEG data
def apply_inverse_operator(raw, inv, lambda2=1.0 / 9.0, method='MNE'):
    """
    Apply the inverse operator to the EEG data.
    
    Parameters:
    raw (mne.io.Raw): The EEG data.
    inv (mne.minimum_norm.InverseOperator): The inverse operator.
    lambda2 (float, optional): The regularization parameter. Defaults to 1.0 / 9.0.
    method (str, optional): The inverse method to use. Defaults to 'sLORETA'.
    
    Returns:
    stc (mne.SourceEstimate): The source estimate.
    """
    stc = mne.minimum_norm.apply_inverse_raw(raw, inv, pick_ori="normal", lambda2=lambda2, method=method)
    return stc

# Extract the time series for each label from the source time courses (stc).
def extract_label_timeseries(stc, src, mode='pca_flip'):
    """
    Extract the time series for each label from the source time courses.

    Parameters:
    subject_name (str): The name of the subject.
    subjects_dir (str): The directory containing the subject data.
    source_estimate (mne.SourceEstimate): The source time courses.
    mode (str, optional): The mode to use for extracting the time series. Defaults to 'pca_flip'.

    Returns:
    stcs (generator): A generator of time series for each label.
    labels (list): The list of labels.
    """

    fs_dir = fetch_fsaverage(verbose=True)
    subjects_dir = op.dirname(fs_dir)
    subject_name = "fsaverage"

    # Read the labels from the annotation file
    labels = mne.read_labels_from_annot(subject_name, parc='aparc', regexp="^(?!unknown).*$", hemi='both', subjects_dir=subjects_dir)

    # Extract the time series for each label
    stcs = mne.extract_label_time_course(stc, labels, src, mode=mode, return_generator=True)

    return stcs, labels
