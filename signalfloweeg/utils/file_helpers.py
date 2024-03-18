import os
import yaml
import requests
from pathlib import Path
from humanize import naturalsize
import pandas as pd

class Catalog:
    """
    A class to load and manage EEG data files and folders.
    """

    def __init__(self, catalog_file_path_or_url=None, suppress_printing=False):
        """
        Initialize the Catalog class.

        Args:
            catalog_file_path_or_url (str, optional): The path to the local YAML file or the URL of the raw GitHub file containing the dataset paths. Defaults to None.
        """
        self.catalog = self.import_catalog(catalog_file_path_or_url, suppress_printing=suppress_printing)
        self._dataset_files = {}
        self._last_dataset_name = None

    def import_catalog(self, file_path_or_url, suppress_printing=False):
        """
        Retrieve the paths of datasets from a local file or a GitHub URL.

        Args:
            file_path_or_url (str): The path to the local YAML file or the URL of the raw GitHub file containing the dataset paths.
            suppress_printing (bool, optional): If True, the method will not print any output. Defaults to False.

        Returns:
            dict: A dictionary containing dataset names as keys and their corresponding paths as values.
        """
        if not suppress_printing:
            print("Loading dataset paths...")

        if file_path_or_url is None:
            if not suppress_printing:
                print("Error: No catalog configuration file available.")
            return {}

        # Determine if the input is a URL or a local file path
        if file_path_or_url.startswith(("http://", "https://")):
            # Fetch the YAML file from the GitHub URL
            response = requests.get(file_path_or_url)
            dataset_paths = yaml.safe_load(response.text)
        else:
            # Load the dataset paths from the specified local YAML file
            with open(file_path_or_url, "r") as file:
                dataset_paths = yaml.safe_load(file)

        if not suppress_printing:
            self.print_catalog(dataset_paths)
        return dataset_paths

    def print_catalog(self, catalog):
        """
        Print the contents of the catalog in a nicely formatted way.

        Args:
            catalog (dict): The catalog dictionary containing dataset names and their corresponding paths.
        """
        # Define color constants
        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        for dataset, path in catalog.items():
            color = GREEN if path else RED
            print(f"{color}{dataset}: {path or 'Dataset not available'}{RESET}")

    def get_location(self, dataset_name):
        """
        Retrieve the file or folder path associated with the given dataset name from the catalog.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            str: The file or folder path associated with the dataset, or None if the dataset is not found in the catalog.
        """
        if self.catalog is None:
            print("Warning: Catalog is not available. Unable to retrieve dataset location.")
            return None

        if dataset_name in self.catalog:
            dataset_path = self.catalog[dataset_name]
            if os.path.isfile(dataset_path):
                return dataset_path
            elif os.path.isdir(dataset_path):
                return dataset_path
            else:
                print(f"Warning: '{dataset_path}' is not a valid file or directory.")
                return None
        else:
            print(f"Warning: Dataset '{dataset_name}' not found in the catalog.")
            return None

    def get_dataset_type(self, dataset_name):
        """
        Determine whether the dataset associated with the given name is a file or a folder.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            str: "file" if the dataset is a file, "folder" if it's a folder, or "unknown" if the path is invalid.
        """
        dataset_location = self.get_location(dataset_name)
        if dataset_location:
            if os.path.isfile(dataset_location):
                return "file"
            elif os.path.isdir(dataset_location):
                return "folder"
            else:
                return "unknown"
        else:
            return "unknown"
        
    def get_associated_fdt_file(self, dataset_location):
        """
        Determine if there is an associated FDT file for the dataset with the given name.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            tuple: A tuple containing the FDT file path and a boolean indicating whether the FDT file is present.
        """
        if dataset_location and dataset_location.lower().endswith(".set"):
            fdt_file_path = os.path.splitext(dataset_location)[0] + ".fdt"
            if os.path.isfile(fdt_file_path):
                return (fdt_file_path, True)
            else:
                return (fdt_file_path, False)
        else:
            return (None, False)
 
    def get_filelist(self, dataset_name, extension=None, return_full_path=True, search_subfolders=True, filename_regex=None, return_as_dataframe=False):
        """
        Retrieve a list of files associated with the given dataset, optionally filtered by file extension, subfolder search, and filename regex.

        Args:
            dataset_name (str): The name of the dataset.
            extension (str, optional): The file extension to filter by (case-insensitive). If not provided, all files will be returned.
            return_full_path (bool, optional): If True, the file paths will be returned as full system paths. If False, the file paths will be returned as relative paths. Defaults to True.
            search_subfolders (bool, optional): If True, the method will search for files in all subfolders of the dataset location. If False, it will only search the top-level folder. Defaults to True.
            filename_regex (str, optional): A regular expression pattern to filter the files by their names. If provided, only the files matching the pattern will be included.
            return_as_dataframe (bool, optional): If True, the method will return the file list as a Pandas DataFrame. If False, it will return a list of dictionaries. Defaults to False.

        Returns:
            Union[list, pd.DataFrame]: A list of dictionaries or a Pandas DataFrame containing the folder path, file name, and file extension for each file associated with the dataset.
        """
        dataset_location = self.get_location(dataset_name)
        if dataset_location and os.path.isdir(dataset_location):
            files = []
            for root, dirs, filenames in os.walk(dataset_location, topdown=not search_subfolders):
                for filename in filenames:
                    if (extension is None or filename.lower().endswith(extension.lower())) and (filename_regex is None or re.match(filename_regex, filename)):
                        file_path = os.path.join(root, filename)
                        if return_full_path:
                            folder_path, file_name = os.path.split(file_path)
                        else:
                            folder_path = os.path.relpath(root, dataset_location)
                            file_name = filename
                        _, ext = os.path.splitext(filename)
                        files.append({"folder_path": folder_path, "file_name": file_name, "extension": ext})
            self._dataset_files = files
            self._last_dataset_name = dataset_name
            if return_as_dataframe:
                return pd.DataFrame(files)
            else:
                return files
        else:
            print(f"Warning: Dataset '{dataset_name}' not found or is not a directory.")
            return pd.DataFrame() if return_as_dataframe else []
                  
    def summarize_filelist(self):
        """
        Provide a summary of the files associated with the given dataset, optionally filtered by file extension.

        Args:
            dataset_name (str): The name of the dataset.
            extension (str, optional): The file extension to filter by (case-insensitive). If not provided, all files will be summarized.

        Returns:
            None
        """


        dataset_files = self._dataset_files
        dataset_name = self._last_dataset_name

        total_size = 0
        file_counts = {}

        # Define color constants
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        RESET = "\033[0m"
        WHITE = "\033[97m"
        BLUE = "\033[94m"

        print(f"{GREEN}Summary for dataset '{dataset_name}'{RESET}")

        if not dataset_files:
            print(f"{RED}No files found for the dataset.{RESET}")
            return

        for file_info in dataset_files:
            file_path = os.path.join(file_info["folder_path"], file_info["file_name"])
            file_size = os.path.getsize(file_path)

            # Check if the file has a .SET extension and add the associated FDT file size
            if file_info["extension"].lower() == ".set":
                fdt_file_path, fdt_file_present = self.get_associated_fdt_file(file_path)
                if fdt_file_present:
                    fdt_file_size = os.path.getsize(fdt_file_path)
                    total_size += fdt_file_size
            elif file_info["extension"].lower() == ".fdt":
                total_size += 0  # Skip FDT files since they are already counted
            else: 
                total_size += file_size

            file_ext = file_info["extension"].lstrip(".")
            if file_ext in file_counts:
                file_counts[file_ext] += 1
            else:
                file_counts[file_ext] = 1

        print(f"{YELLOW}Total number of files: {len(dataset_files)}{RESET}")
        print(f"{YELLOW}Total size: {naturalsize(total_size)}{RESET}")

        print(f"{GREEN}File type breakdown:{RESET}")
        for file_ext, count in file_counts.items():
            print(f"  {BLUE}{file_ext.upper()}: {count}{RESET}")
            

    def create_yaml_template(self, output_path=None):
        """
        Create a YAML template file with the basic structure of dataset names and file paths.

        Args:
            output_path (str, optional): The path to the output YAML file. If not provided, the template will be created in the current directory with the name "catalog_template.yml".
        """
        if output_path is None:
            output_path = os.path.join(os.getcwd(), "catalog_template.yml")

        template_data = {
            "dataset1": "/path/to/dataset1",
            "dataset2": "/path/to/dataset2",
            "dataset3": "/path/to/dataset3"
        }

        with open(output_path, "w") as file:
            file.write("# SignalFlowEeeg Catalog of datasets\n")
            file.write("# Replace the following dataset names with your actual dataset names\n")
            file.write("# Replace the following file paths with the actual locations of your datasets\n")
            file.write("# Specify either a file name or file path for each dataset\n")
            yaml.dump(template_data, file, default_flow_style=False)

        print(f"YAML template created at: {output_path}")