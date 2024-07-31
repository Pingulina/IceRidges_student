# functions to simulate the deepest ridge
import numpy as np
import matplotlib.pyplot as plt
import os
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
constants = import_module('constants', 'helper_functions')
load_data = import_module('load_data', 'data_handling')
mooring_locs = import_module('mooring_locations', 'helper_functions')

def simulate_deepest_ridge(year=None, loc=None, dict_mooring_locations=None):
    """simulate the deepest ridge
    param year: int, the year for the level ice analysis
    param loc: str, the location for the level ice analysis
    param dict_mooring_locations: dict, dictionary with the mooring locations
    return None
    """
    pathName_ridgeStatistics = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')
    
    if dict_mooring_locations is None:
        dict_mooring_locations = mooring_locs.mooring_locations(storage_path='Data') # dictionary with the mooring locations


    # get the year and location from the user, if they are not provided
    list_years = [int(season.split('-')[0]) for season in list(dict_mooring_locations.keys())]
    list_seasons = list(dict_mooring_locations.keys())

    if year is None:
        while True:
            year = int(input("Enter the year for the level ice analysis: "))
            if year in list_years:
                break
            else:
                print(f"The year {year} is not in the mooring data. Possible years are: {list_years}")
    if loc is None:    
        while True:
            loc = input("Enter the location for the level ice analysis: ")
            if loc in dict_mooring_locations[list_seasons[list_years.index(year)]].keys():
                break
            else:
                print(f"The location {loc} is not in the mooring data. Possible locations are: {list(dict_mooring_locations[list_seasons[list_years.index(year)]].keys())}")
    dateNum, draft, dict_ridge_statistics, year, loc = load_data.load_data_oneYear(path_to_json_processed=pathName_ridgeStatistics, 
                                                                                   path_to_json_mooring=path_to_json_mooring, year=year, loc=loc, 
                                                                                   skip_nonexistent_locs=True)
    
    level_ice_deepest_mode = dict_ridge_statistics[loc]['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics[loc]['level_ice_expect_deepest_mode']
    level_ice_mode = dict_ridge_statistics[loc]['level_ice_mode'] # needs to be done
    draft_deeply_weekest_ridge = dict_ridge_statistics[loc]['draft_weekly_deepest_ridge']
    number_ridges = dict_ridge_statistics[loc]['number_ridges']
    mean_keel_draft = dict_ridge_statistics[loc]['mean_keel_draft']

    # initialize the plot for tracking steps of calculations
    plt.ion() # interactive mode on to see updates of plot
    fig_overview = plt.figure(figsize=(10, 6))
    grid_spec = fig_overview.add_gridspec(3, 2)

    # plot level ice draft and weekly deepest ridge draft


