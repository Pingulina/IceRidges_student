# load data from json file for specific year and location

import os
import sys
import json
import numpy as np

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
j2d = import_module('jsonified2dict', 'data_handling')


def load_data_oneYear(year=None, loc=None, path_to_json_processed=None, path_to_json_mooring=None, load_dict_ridge_statistics=True, skip_nonexistent_locs=False, robustOption=True):
    """
    load the data from one year.
    If no robust option is chosen, the location is not checked. Only do this if you know the location exists
    year: int, the year you want to analyse
    loc: str, the location you want to analyse
    path_to_json_processed: str, the path to the processed json files
    path_to_json_mooring: str, the path to the mooring json files
    load_dict_ridge_statistics: bool, if True, the ridge statistics are loaded from the json file
    robustOption: bool, if True, the location is checked if it exists in the mooring_locations.json file.
    :return: dateNum, draft, dict_ridge_statistics, year, loc
"""
    
    if path_to_json_processed is None:
        pathName = os.getcwd()
        path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    if path_to_json_processed is None:
        path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    
    dict_ridge_statistics = {}

    while True:
        if year is None:
            year = input("Enter the year you want to analyse: ")
        try:
            year = int(year)
        except ValueError:
            print("Wrong format. Please enter a valid year")
            year = None
            continue
        
        if loc is None:
            loc = input("Enter the location you want to analyse: ")
            # check, if there is a json file for the year and location
        
        json_file_name_processed = f"ridge_statistics_{year}{loc}.json"
        if not os.path.exists(os.path.join(path_to_json_processed, json_file_name_processed)):
            if skip_nonexistent_locs:
                print(f"The json file ridge_statistics_{year}{loc}.json does not exist. Skipping this location.")
                return None, None, None, year, loc
            print(f"The json file ridge_statistics_{year}{loc}.json does not exist. Please enter a valid year and location.")
            year = None
            loc = None
            continue

        if load_dict_ridge_statistics:
            # load the ridge statistics from the json file
            with open(os.path.join(path_to_json_processed, json_file_name_processed), 'r') as file:
                dict_ridge_statistics[loc] = j2d.jsonified2dict(json.load(file))
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
                
            
        else:
            dict_ridge_statistics = None
            # if robustOption: # if no robust option is chosen, the location is not checked. Only do this if you know the location exists
            #     # load mooring_locations.json from Data to check, if the location exists
            #     with open(os.path.join(os.path.join(os.getcwd(), 'Data'), 'mooring_locations.json'), 'r') as file:
            #         dict_locations = json.load(file)
            #         locations_this_year = dict_locations.keys()
            #         locations_this_year = dict_locations[list(dict_locations.keys())[np.where([int(key[0:4]) == year for key in dict_locations.keys()])[0][0]]].keys()
            #     if loc is None:
            #         loc = input("Enter the location you want to analyse: ")
            #     if loc in locations_this_year:
            #         break
            #     else:
            #         print(f"The location you entered is not in the data. Please enter a valid location. The locations for this year are: {locations_this_year}")
            #         loc = None
            #         continue
            # else:
            #     # if no robust option is chosen, the location is not checked. Only do this if you know the location exists
            #     break
    
        break # end the while loop (this is only reached, if the year and location are valid)
    
    # get the raw data for the year and location
    with open(os.path.join(path_to_json_mooring, f"mooring_{year}-{year+1}_{loc}_draft.json"), 'r') as file:
        mooring_draft_dict = j2d.jsonified2dict(json.load(file))
    # _, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json_mooring, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)
    dateNum = mooring_draft_dict[loc]['dateNum']
    draft = mooring_draft_dict[loc]['draft']

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
        file_name_components = file.split('.')
        file_name = file_name_components[0]
        if len(file_name_components) > 1:
            file_type = file_name_components[1]
        else:
            break # this is a folder
        if file_name.split('_')[1] == 'statistics' and file_type == 'json':
            year = int(file_name.split('_')[2][0:4])
            loc = file_name.split('_')[2][4:]
            try:
                assert len(dict_ridge_statistics_year_all[year].keys()) > 0
            except KeyError:
                dict_ridge_statistics_year_all[year] = {}
            except AssertionError:
                dict_ridge_statistics_year_all[year] = {}
            with open(os.path.join(path_to_json_processed, file), 'r') as file:
                dict_ridge_statistics_year = json.load(file)
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
            dict_ridge_statistics_year_all[year][loc] =  j2d.jsonified2dict(dict_ridge_statistics_year)

    return dict_ridge_statistics_year_all
 
