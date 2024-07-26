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
lis = import_module('level_ice_statistics', 'data_analysis')
mooring_locs = import_module('mooring_locations', 'helper_functions')
user_input_iteration = import_module('user_input_iteration', 'user_interaction')


def level_ice_statistics_multiYear():
    """iterate over multiple years and locations and run the level_ice_statistics function"""
    dict_mooring_locations = mooring_locs.mooring_locations(storage_path='Data') # dictionary with the mooring locations
    list_years = [int(season.split('-')[0]) for season in list(dict_mooring_locations.keys())] # list of years
    list_seasons = list(dict_mooring_locations.keys()) # list of seasons
    year_ind = 0 # index for the year
    year = int(list_years[year_ind]) # choose the first year
    season = list_seasons[list_years.index(year)] # corresponding season
    loc_ind = 0 # index for the location
    loc = list(dict_mooring_locations[str(season)].keys())[loc_ind] # choose the first location
    # let the user choose the years and locations (iterating over them)
    while True:
        # let the user choose the year
        print(f"Current year is {year}. \nPress 'f' for next YEAR, 'd' for this year and 's' for last year and 'x' to exit the program. You can also enter the year directly. In all cases, press enter afterwards.")
        success, year_ind = user_input_iteration.get_user_input_iteration(year_ind, len(list_years))
        year = list_years[year_ind]
        if success == -1:
            break
        elif success == 0:
            continue
        elif success == 1:
            pass
        else:
            raise ValueError("Invalid success value.")
        
        # get the corresponding season
        season = list_seasons[list_years.index(year)]
        print(f"Choosen season is {season}.")
        
        while True:
            # let the user choose the location
            print(f"Current location is {loc}. \nPress 'f' for next LOCATION, 'd' for this location and 's' for last location and 'x' to exit the program. You can also enter the location directly. In all cases, press enter afterwards.")
            success, loc_ind = user_input_iteration.get_user_input_iteration(loc_ind, len(dict_mooring_locations[season]))
            loc = list(dict_mooring_locations[season].keys())[loc_ind]
            if success == -1:
                break
            elif success == 0:
                continue
            elif success == 1:
                pass
            else:
                raise ValueError("Invalid success value.")
            
            # user has to confirm the year and location
            choose_this = input(f"Do you want to run level_ice_statistics for year {year} and location {loc}? Press 'y' for yes and 'n' for no. Press enter afterwards.")
            if choose_this == 'y' or choose_this == 'Y':
                print(f"Running level_ice_statistics for year {year} and location {loc}.")
                lis.level_ice_statistics(year=year, loc=loc, dict_mooring_locations=dict_mooring_locations)
            elif choose_this == 'n' or choose_this == 'N':
                print("Ok, let's choose another year and location.")
                continue
            else:
                print("I understand only 'y' and 'n'.")
                continue

    print("Bye!")