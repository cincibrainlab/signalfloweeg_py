import os
import csv
import fnmatch

def find_set_files(directory):
    """
    Search for .set files in all subdirectories of the given directory.
    Returns a list of tuples containing the basename and folder of each .set file found.
    """
    set_files = []
    for root, dirs, files in os.walk(directory):
        for file in fnmatch.filter(files, '*.set'):
            set_files.append((os.path.basename(file), root))
    return set_files

def create_csv(file_list, output_file='set_files_list.csv'):
    """
    Create a CSV file listing all .set files found, including their basename, folder, and subfolder.
    """
    with open(output_file, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(['Filename', 'Folder', 'Subfolder'])
        for file in file_list:
            folder_path = file[1]
            subfolder = os.path.basename(folder_path)
            parent_folder = os.path.basename(os.path.dirname(folder_path))
            filewriter.writerow([file[0], parent_folder, subfolder])
            
if __name__ == "__main__":
    directory = input("Enter the directory to search for .set files (leave blank for current directory): ")
    if not directory:
        directory = os.getcwd()
    set_files = find_set_files(directory)
    if set_files:
        create_csv(set_files)
        print(f"CSV file has been created listing {len(set_files)} .set files found.")
    else:
        print("No .set files found in the specified directory.")
