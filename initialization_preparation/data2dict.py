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


def data2dict(file_path, file_name):
    """
    Convert the data from a .dat file to a dictionary and store it in a .json file
    :param file_path: str, path to the .dat file
    :return: dict, dictionary with the data
    """
    print(f"Converting data from {file_name} to dict")
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
    for i, line in enumerate(data[2:]):
        date, time, draft = line.split() # write split(',') to enable csv reading
        data_dict['date'].append(int(date))
        data_dict['time'].append(int(time))
        # convert date and time to a date number (0 is 1.1.0000 00:00:00, 0.5 is 1.1.0000 12:00:00, ...)
        data_dict['dateNum'].append(dts.datenum(date, time)) # use strings, otherwise there are not always enough digits
        data_dict['draft'].append(float(draft))

    return data_dict

def json2dict(file_path, file_name):
    """
    Load the .json data to a dictionary
    :param file_path: str, path to the .json file
    :param file_name: str, name of the .json file
    :return: dict, dictionary with the data
    """
    print(f"Converting data from {file_name} to dict")
    file_path_name = os.path.join(file_path, file_name)
    with open(file_path_name, 'r') as file:
        data_dict = json.load(file)
    return data_dict
    


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
    path_name = os.path.join(os.getcwd(), 'Data_Beaufort_Gyre_Exploration')
    file_path_list = [os.path.join(path_name, thisSeason) for thisSeason in ['2004-2005', '2005-2006', '2006-2007']]
    # file_path_list = [file_path_helper(path_name, thisSeason) for thisSeason in ['2004-2005', '2005-2006', '2006-2007']] # ['2004-2005', '2005-2006', '2006-2007']]
    return data2dict(file_path_list[0], 'uls04a_draft.dat')


if __name__ == "__main__":
    print(example())
    print('Done!')