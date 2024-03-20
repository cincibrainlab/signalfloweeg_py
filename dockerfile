FROM jupyter/scipy-notebook:latest

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 && \
    rm -rf /var/lib/apt/lists/*

# Install mamba for faster conda package installation
RUN conda install -n base -c conda-forge mamba

# Install MNE and its dependencies using mamba
RUN mamba install -c conda-forge \
    mne \
    pyvista \
    vtk \
    panel \
    holoviews \
    ipywidgets \
    ipyvolume \
    pyopengl \
    nodejs \
    nibabel \
    h5py \
    pyedflib \
    plotly \
    altair \
    bokeh && \
    mamba clean -afy

# Install Jupyter Notebook plugin widgets
RUN mamba install -c conda-forge \
    widgetsnbextension \
    ipympl \
    jupyter-matplotlib \
    ipyfilechooser \
    ipysheet \
    ipytree \
    bqplot \
    ipyleaflet \
    jupyter_nbextensions_configurator && \
    mamba clean -afy

# Enable Jupyter Notebook plugin widgets and extensions
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix && \
    jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
    jupyter labextension install jupyter-matplotlib && \
    jupyter labextension install ipysheet && \
    jupyter labextension install ipytree && \
    jupyter labextension install bqplot && \
    jupyter labextension install jupyter-leaflet && \
    jupyter nbextensions_configurator enable --user

# Set environment variables
ENV JUPYTER_ENABLE_LAB=yes

# Copy sample datasets and notebooks
COPY sample_data /home/jovyan/sample_data
COPY notebooks /home/jovyan/notebooks

# Set up Jupyter Notebook configuration
COPY jupyter_notebook_config.py /etc/jupyter/

# Expose the Jupyter port
EXPOSE 8888

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root"]