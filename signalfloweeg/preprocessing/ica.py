import mne
from mne.preprocessing import ICA

def run_ICA(data: mne.io.Raw, method: str = "fastica", n_components: int = None, max_iter: str = "auto", random_state: int = 97):
    """ 
    Run 

    Parameters:
    - data (mne.io.Raw): Input data object.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # if n_components == None:
    #     # TODO Change magic number later 
    #     n_components = len(data._data) - 1
    #     n_components = 0.999999
    # Function implementation goes here
    data.load_data()
    ica = ICA(n_components=n_components, max_iter=max_iter, random_state=random_state, method=method)
    ica.fit(data)
    return data, ica

def show_ICA(data: mne.io.Raw, ICA: mne.preprocessing.ICA):
    """
    Show the ICA components.

    Parameters:
    - data (mne.io.Raw): Input data object.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # Function implementation goes here
    ICA.plot_components()
    ICA.plot_sources(data)
    ICA.plot_properties(data)
    return data