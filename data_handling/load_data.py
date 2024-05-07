# load data from json file for specific year and location

import os
import sys
import json

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
# Get the current working directory
cwd = os.getcwd()
# Construct the path to the base directory
base_dir = os.path.join(cwd, '..')
# Add the base directory to sys.path
sys.path.insert(0, base_dir)
from import_module import import_module
### imports using the helper function import_module
j2np = import_module('json2numpy', 'data_handling')
constants = import_module('constants', 'helper_functions')
j2d = import_module('jsonified2dict', 'initialization_preparation')


def load_data_oneYear(year=None, loc=None, path_to_json_processed=None, path_to_json_mooring=None, load_dict_ridge_statistics=True):
    
    if path_to_json_processed is None:
        pathName = os.getcwd()
        path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    if path_to_json_processed is None:
        path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')

    while True and load_dict_ridge_statistics:
        if year is None:
            year = input("Enter the year you want to analyse: ")
        try:
            year = int(year)
        except ValueError:
            print("Wrong format. Please enter a valid year")
            year = None
            continue
        

        json_file_name_processed = f"ridge_statistics_{year}.json"
        # check if the json file exists
        if not os.path.exists(os.path.join(path_to_json_processed, json_file_name_processed)):
            print(f"The json file {json_file_name_processed} does not exist. Please enter a valid year.")
            continue
        # load the ridge statistics from the json file
        with open(os.path.join(path_to_json_processed, json_file_name_processed), 'r') as file:
            dict_ridge_statistics = json.load(file)
            # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
            for loc_dict in dict_ridge_statistics.keys():
                dict_ridge_statistics[loc_dict] = j2d.jsonified2dict(dict_ridge_statistics[loc_dict])

            
        
        locations_this_year = dict_ridge_statistics.keys() 
        if loc is None:
            loc = input("Enter the location you want to analyse: ")
        if loc in locations_this_year:
            break
        else:
            print(f"The location you entered is not in the data. Please enter a valid location. The locations for this year are: {locations_this_year}")
            loc = None
            continue
    
    
    
    # get the raw data for the year and location
    _, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json_mooring, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)

    return dateNum, draft, dict_ridge_statistics, year, loc
    
    
    # get the data for all years and locations each in an array
    # in Data_results/ridge_statistics/ridge_statistics_{year}.json the data is stored in the following format:
    # dict_ridge_statistics = {loc1: {'data_name' : data, 'data_name' : data, ... }, loc2: {'data_name' : data, 'data_name' : data, ...}, ...}

def load_data_all_years(path_to_json_processed=None):
    # list all files in the directory
    files = os.listdir(path_to_json_processed)
    # sort the files by year
    files.sort()
    dict_ridge_statistics_year_all = {}
    for file in files:
        file_name = file.split('.')[0]
        if file_name.split('_')[1] == 'statistics':
            year = int(file_name.split('_')[2])
            with open(os.path.join(path_to_json_processed, file), 'r') as file:
                dict_ridge_statistics_year = json.load(file)
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
                for loc_year in dict_ridge_statistics_year.keys():
                    dict_ridge_statistics_year[loc_year] = j2d.jsonified2dict(dict_ridge_statistics_year[loc_year])

            dict_ridge_statistics_year_all[year] = dict_ridge_statistics_year


    return dict_ridge_statistics_year_all
 
