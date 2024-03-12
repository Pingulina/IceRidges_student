# The data stored in .dat files with format date (int), time (int), draft (float) is converted to a dictionary and stored in a .json file.
import os
import json
import sys

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
# Get the current working directory
cwd = os.getcwd()
# Construct the path to the base directory
base_dir = os.path.join(cwd, '..')
# Add the base directory to sys.path
sys.path.insert(0, base_dir)
from import_module import import_module
### imports using the helper function import_module
# import the date_time_stuff module from the helper_functions directory
dts = import_module('date_time_stuff', 'helper_functions')


def data2json(file_path, file_name, storage_path):
    """
    Convert the data from a .dat file to a dictionary and store it in a .json file
    :param file_path: str, path to the .dat file
    :return: None
    """
    print(f"Converting data from {file_name} to .json")
    # read the data from the .dat file
    file_dat = os.path.join(file_path, file_name)
    with open(file_dat, 'r') as file:
        data = file.readlines()
    # convert the data to a dictionary
    data_dict = {}
    # skip the first two lines, as they contain the header
    data_dict['position_info'] = data[0]
    data_dict['date'] = []
    data_dict['time'] = []
    data_dict['dateNum'] = []
    data_dict['draft'] = []
    for line in data[2:]:
        date, time, draft = line.split() # write split(',') to enable csv reading
        data_dict['date'].append(int(date))
        data_dict['time'].append(int(time))
        # convert date and time to a date number (0 is 1.1.0000 00:00:00, 0.5 is 1.1.0000 12:00:00, ...)
        data_dict['dateNum'].append(dts.datenum(date, time)) # use strings, otherwise there are not always enough digits
        data_dict['draft'].append(float(draft))
    # store the data in a .json file
    storage_name = file_name.replace('.dat', '.json')
    file_storage = os.path.join(storage_path, storage_name)
    # if the storage path does not exist, create it
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    with open(file_storage, 'w') as file:
        json.dump(data_dict, file)

    print(f"Data from {file_name} stored in {file_storage}")
    return None

def data2json_multi(file_path_list, storage_path_folder):
    """Transform multiple .dat files to .json files
    The function takes all dat files from the file_path_list and stores the json files in the storage_path_list
    :param file_path_list: list, list of file paths
    :param storage_path_folder: path to the folder where the folders for each season containing the .json files are stored
    :return: None
    """
    # iterate over file_path_list and find all .dat files
    for file_path in file_path_list:
        # create the storeage path for the current file_path
        # get the current season from the file_path (e.g. 2004-2005)
        current_season = file_path.split(os.sep)[-2]
        print(f"Converting .dat files from {current_season}")
        # add the current seasen (e.g. 2004-2005) to the storage_path_folder
        storage_path = os.path.join(storage_path_folder, current_season)
        for file in os.listdir(file_path):
            if file.endswith('.dat'):
                data2json(file_path, file, storage_path)

    print("All .dat files converted to .json")
    return None

def data2json_interactive(file_path_list, storage_path_folder, overwrite=None):
    """Transform multiple .dat files to .json files
    Asking the user if he wants to proceed, if there is already a file with the same name in the storage path
    :param file_path_list: list, list of file paths
    :param storage_path_folder: path to the folder where the folders for each season containing the .json files are stored
    :param overwrite: (optional), bool, if True, the function will overwrite existing files, if False, the functtion will skip exisitng files. If None the user will be asked if he wants to proceed
    :return: None
    """
    # iterate over file_path_list and find all .dat files
    for file_path in file_path_list:
        # create the storeage path for the current file_path
        # get the current season from the file_path (e.g. 2004-2005)
        current_season = file_path.split(os.sep)[-2]
        print(f"Converting .dat files from {current_season}")
        # add the current seasen (e.g. 2004-2005) to the storage_path_folder
        storage_path = os.path.join(storage_path_folder, current_season)
        for file in os.listdir(file_path):
            if file.endswith('.dat'):
                # check if the file is already stored in the storage_path
                storage_name = file.replace('.dat', '.json')
                file_storage = os.path.join(storage_path, storage_name)
                if os.path.exists(file_storage):
                    # ask the user if he wants to proceed or skip this file
                    if overwrite is None:
                        proceed = input(f"-----------\nThe file \n    {storage_name} \nalready exists in {storage_path}. \nDo you want to transform it anyway and overwrite the current file (Y/y) or skip this file (N/n)?")
                    else: 
                        proceed = 'Y' if overwrite else 'N'
                    if proceed == 'Y' or proceed == 'y':
                        data2json(file_path, file, storage_path)
                    else:
                        print(f"The file {storage_name} was not converted to .json")
                        continue
                else:
                    data2json(file_path, file, storage_path)

    print("All .dat files converted to .json")
    return None

def file_path_helper(path_name, season):
    """Create the file path for the given season and path_name
    :param path_name: str, name of the path, with written SEASON where the season should be inserted
    :param season: str, name of the season
    :return: str, path to the folder
    """
    return path_name.replace('SEASON', season)


def example():
    this_file_path = os.path.abspath(os.getcwd())
    # storage_path = os.path.join(this_file_path, 'Data', 'mooring_data')
    # data2json(file_path, file_name, storage_path)
    path_name = r"C:\Users\cls8575\Documents\NTNU\IceRidges-main\Data_Beaufort_Gyre_Exploration_Project\SEASON\dat_files"
    file_path_list = [file_path_helper(path_name, thisSeason) for thisSeason in ['2005-2006']] # ['2004-2005', '2005-2006', '2006-2007']]
    storage_path_folder = os.path.join(this_file_path, 'Data', 'mooring_data')
    data2json_interactive(file_path_list, storage_path_folder)
    return None