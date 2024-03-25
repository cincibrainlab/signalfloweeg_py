---
title: "Exploring the Catalog Class for EEG Data Management"
format: html
---

## Introduction

Welcome to this tutorial on the `Catalog` class, a powerful tool for managing your EEG data files. The `Catalog` class is part of the `signalfloweeg` library, which aims to enhance the reproducibility and consistency of EEG data analysis.

In this notebook, we'll explore the various features of the `Catalog` class and how it can help you streamline your EEG data workflow.

## Importing the Catalog Class

First, let's import the `Catalog` class from the `signalfloweeg.utils` module:

```python
from signalfloweeg.utils import Catalog
```

## Creating a Catalog Instance

The `Catalog` class is used to manage a collection of EEG datasets. You can initialize a `Catalog` instance by providing the path to a YAML file or a URL that contains the dataset information.

```python
# Load the catalog from a local YAML file
catalog = Catalog("path/to/your/catalog.yml")

# Load the catalog from a GitHub URL
catalog = Catalog("https://tinyurl.com/yfudj62c")
```

## Exploring the Catalog

Once you have a `Catalog` instance, you can use its various methods to interact with the dataset information.

### Retrieving Dataset Locations

The `get_location` method allows you to retrieve the file or folder path associated with a specific dataset:

```python
# Get the location of a dataset
dataset_location = catalog.get_location("demo_rest_state")
print(dataset_location)
```

### Determining Dataset Types

The `get_dataset_type` method can be used to determine whether a dataset is a file or a folder:

```python
# Check the type of a dataset
dataset_type = catalog.get_dataset_type("proj_ketamine")
print(dataset_type)
```

### Checking for Associated FDT Files

If you have a dataset with a `.SET` extension, you can use the `get_associated_fdt_file` method to check if there is an associated FDT file:

```python
# Check for an associated FDT file
fdt_file_path, fdt_file_present = catalog.get_associated_fdt_file("demo_rest_state")
if fdt_file_present:
    print(f"Associated FDT file: {fdt_file_path}")
else:
    print("No associated FDT file found.")
```

### Retrieving File Lists

The `get_filelist` method allows you to retrieve a list of files associated with a specific dataset, optionally filtered by file extension, subfolder search, and filename regex:

```python
# Retrieve the files for a dataset, filtering by extension
dataset_files = catalog.get_filelist("demo_rest_state", extension=".set")
for file_info in dataset_files:
    print(f"Folder path: {file_info['folder_path']}")
    print(f"File name: {file_info['file_name']}")
    print(f"Extension: {file_info['extension']}")
    print()
```

### Summarizing File Lists

The `summarize_filelist` method provides a visual summary of the files associated with a dataset, including the total number of files, total size, and file type breakdown:

```python
# Summarize the files for a dataset
catalog.summarize_filelist()
```

### Creating a YAML Template

The `create_yaml_template` method allows you to generate a YAML template file with sample dataset names and file paths, which you can then customize with your own dataset information:

```python
# Create a YAML template file
catalog.create_yaml_template()
```

## Conclusion

The `Catalog` class provides a comprehensive set of tools for managing your EEG data files. By using this class, you can streamline your data loading process, ensure consistency across your analysis workflows, and improve the overall reproducibility of your research.