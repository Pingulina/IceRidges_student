# analysing the restults of the ridge statistics function

import os
import numpy as np
import sys
import matplotlib.pyplot as plt

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
j2np = import_module('json2numpy', 'data_handling')


def weekly_visual_analysis(dict_ridge_statistics:dict):
    """
    """
    pathName = os.getcwd()
    path_to_json = os.path.join(pathName, 'Data', 'uls_data')
    while True:
        year = input("Enter the year you want to analyse: ")
        try:
            year = int(year)
            assert year in dict_ridge_statistics.keys()
        except ValueError:
            print("Wrong format. Please enter a valid year")
            continue
        except AssertionError:
            print("The year you entered is not in the data. Please enter a valid year.")
            continue
        locations_this_year = dict_ridge_statistics[str(year)].keys() 
        loc = input("Enter the location you want to analyse: ")
        if loc in locations_this_year:
            break
        else:
            print(f"The location you entered is not in the data. Please enter a valid location. The locations for this year are: {locations_this_year}")
            continue
        
    # get the raw data for the year and location
    _, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)
    # get the processed data for the year and location
    data = dict_ridge_statistics[str(year)][loc]

    # plot the data
    figure_weekly_analysis = plt.figure(layout='constrained', figsize=(12,9))
    gridspec_weekly_analysis = figure_weekly_analysis.add_gridspec(4,2)

    # figure ice data
    ax_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0:2,0])
    ax_ice_data.set_ylim(0, 30)

    patch_current_week_ice_data = ax_ice_data.fill_between(dateNum, 0, draft, color='lightblue', label='Current week ice data')
    ULS_draft_signal = ax_ice_data.plot(dateNum, draft, color='black', label='Raw ULS draft signal')
    RidgePeaks = ax_ice_data.scatter(dict_ridge_statistics[year][loc]['keel_dateNum'], dict_ridge_statistics[year][loc]['keel_draft'], color='red', label='Individual ridge peaks')
    LI_thickness = ax_ice_data.step(dict_ridge_statistics[year][loc]['keel_dateNum'], dict_ridge_statistics[year][loc]['level_ice_deepest_mode'], where='mid', color='green', label='Level ice draft estimate')

    ax_ice_data.legend()

    # figure current week ice data
    ax_current_week_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,0])
    ax_current_week_ice_data.set_ylim(0, 30)
    
    RidgePeaks_thisWeek = ax_ice_data.scatter(dict_ridge_statistics[year][loc]['keel_dateNum'], dict_ridge_statistics[year][loc]['keel_draft'], color='red', label='Individual ridge peaks')
    LI_thickness_thisWeek = ax_ice_data.step(dict_ridge_statistics[year][loc]['keel_dateNum'], dict_ridge_statistics[year][loc]['level_ice_deepest_mode'], where='mid', color='green', label='Level ice draft estimate')


    # figure mean ridge keel depth
    ax_mean_ridge_keel_depth = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0,1])

    # figure I don't know yet
    ax_ = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[1,1])

    # figure weekly deepest ridge
    ax_weekly_deepest_ridge = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2,1])

    # figure number of ridges
    ax_number_of_ridges = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[3,1])


