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
    return ica

def manual_component_removal(data: mne.io.Raw, ICA: mne.preprocessing.ICA):
    """
    Show the ICA components.

    Parameters:
    - data (mne.io.Raw): Input data object.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # Function implementation goes here
    # TODO Make a way to type in the components to remove
    ICA.plot_sources(data, block=True, theme='light')
    
def remove_ICA(data: mne.io.Raw, ICA: mne.preprocessing.ICA, components: list):
    """
    Remove the ICA components.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - ICA (mne.preprocessing.ICA): ICA object.
    - components (list): List of components to remove.

    Returns:
    - mne.io.Raw: Output data object.
    """
    # Function implementation goes here
    data = ICA.apply(data, exclude=components)
    return data

def save_ICA(ICA: mne.preprocessing.ICA, filename: str):
    """
    Save the ICA object.

    Parameters:
    - ICA (mne.preprocessing.ICA): ICA object.
    - filename (str): Filename to save the ICA object.

    Returns:
    - None
    """
    # Function implementation goes here
    ICA.save(filename)
    
def load_ICA(filename: str):
    """
    Load the ICA object.

    Parameters:
    - filename (str): Filename to load the ICA object.

    Returns:
    - mne.preprocessing.ICA: ICA object.
    """
    # Function implementation goes here
    return ICA.read(filename)

def plot_ICA(data: mne.io.Raw, ICA: mne.preprocessing.ICA):
    """
    Plot the ICA object.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - ICA (mne.preprocessing.ICA): ICA object.

    Returns:
    - None
    """
    # Function implementation goes here
    ICA.plot_components(data)
    
def plot_ICA_overlay(data: mne.io.Raw, ICA: mne.preprocessing.ICA):
    """
    Plot the ICA object overlay.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - ICA (mne.preprocessing.ICA): ICA object.

    Returns:
    - None
    """
    # Function implementation goes here
    ICA.plot_overlay(data)
    
def plot_ICA_properties(data: mne.io.Raw, ICA: mne.preprocessing.ICA):
    """
    Plot the ICA object properties.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - ICA (mne.preprocessing.ICA): ICA object.

    Returns:
    - None
    """
    # Function implementation goes here
    ICA.plot_properties(data)
    
def plot_ICA_sources(data: mne.io.Raw, ICA: mne.preprocessing.ICA):
    """
    Plot the ICA object sources.

    Parameters:
    - data (mne.io.Raw): Input data object.
    - ICA (mne.preprocessing.ICA): ICA object.

    Returns:
    - None
    """
    # Function implementation goes here
    ICA.plot_sources(data)