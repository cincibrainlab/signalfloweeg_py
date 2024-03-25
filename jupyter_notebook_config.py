import os
from jupyter_core.paths import jupyter_data_dir

# Set the Jupyter Notebook directory
c.NotebookApp.notebook_dir = '/home/jovyan/notebooks'

# Set the Jupyter Notebook port
c.NotebookApp.port = 8888

# Set the Jupyter Notebook IP address
c.NotebookApp.ip = '0.0.0.0'

# Disable the Jupyter Notebook password
c.NotebookApp.password = ''
c.NotebookApp.token = ''

# Enable the Jupyter Notebook extensions
c.NotebookApp.nbserver_extensions = {
    'widgetsnbextension': True,
    'ipywidgets.nbextension': True,
    'ipympl.nbextension': True,
    'jupyter_nbextensions_configurator': True
}

# Set the Jupyter Notebook theme
c.JupyterLabTheme.theme = 'light'

# Set the Jupyter Notebook file chooser
c.FileChooser.show_hidden = True

# Set the Jupyter Notebook log level
c.Application.log_level = 'INFO'

# Set the Jupyter Notebook log file
c.NotebookApp.log_file = os.path.join(jupyter_data_dir(), 'notebook.log')