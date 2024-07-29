# provides a function to check the minimum mode intensity threshold and adjust it if necessary

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

def mode_threshold_analysis(year=None, loc=None, dict_mooring_locations=None):
    """check the minimum mode intensity threshold and adjust it if necessary"""
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
    draft_deeply_weekest_ridge = dict_ridge_statistics[loc]['draft_weekly_deepest_ridge']
    number_ridges = dict_ridge_statistics[loc]['number_ridges']
    peaks_intensity = dict_ridge_statistics[loc]['peaks_intensity']
    peaks_location = dict_ridge_statistics[loc]['peaks_location']

    # initialize the plot
    figure_modeThreshold = plt.figure(figsize=(10, 6))
    # initialize grid for the plot
    grid_modeThreshold = figure_modeThreshold.add_gridspec(2, 2)
    # initialize the color array. First, all points will have the same color. But if points are sorted out due to too less occurance, they can't be kicked out of the plot, so make them white instead
    color_array = np.full(np.shape(draft_deeply_weekest_ridge), 'b')
    # add the subplots
    x = np.arange(0, 3, 0.0001) # x-values to visualize the mode threshold
    # plot with weekly maximum ridge keel draft over level ice expected deepest mode 
    ax1 = figure_modeThreshold.add_subplot(grid_modeThreshold[0, 0])
    ax1.scatter(level_ice_expect_deepest_mode, draft_deeply_weekest_ridge, c='b', label='deepest mode')
    ax1.plot(x, 20*np.sqrt(x), 'r--', label='20*sqrt(x)')
    ax1.plot(x, 7.55+4.83*x, 'g', label='7.55+4.83*x')
    ax1.set_xlabel('level ice thickness [m]')
    ax1.set_ylabel('deepest mode keel draft [m]')
    ax1.set_title(f'Deepest mode keel draft over LI expected deepest mode for {loc} in {year}')

    # plot with the maximum ridge keel draft over the level ice deepst mode
    ax2 = figure_modeThreshold.add_subplot(grid_modeThreshold[0, 1])
    ax2.scatter(level_ice_deepest_mode, draft_deeply_weekest_ridge, c='b', label='deepest_mode')
    ax2.plot(x, 20*np.sqrt(x), 'r--', label='20*sqrt(x)')
    ax2.plot(x, 7.55+4.83*x, 'g', label='7.55+4.83*x')
    ax2.set_xlabel('level ice thickness [m]')
    ax2.set_ylabel('deepest mode keel draft [m]')
    ax2.set_title(f'Deepest mode keel draft over LI deepest mode for {loc} in {year}')

    # plot with the maximum ridge keel draft over the level ice deepst mode; in this plot the threshold will be adjusted in the while loop
    ax3 = figure_modeThreshold.add_subplot(grid_modeThreshold[1, 1])
    scatter3 = ax3.scatter(level_ice_deepest_mode, draft_deeply_weekest_ridge, c=color_array, label='deepest_mode')
    ax3.plot(x, 20*np.sqrt(x), 'r--', label='20*sqrt(x)')
    ax3.plot(x, 7.55+4.83*x, 'g', label='7.55+4.83*x')
    ax3.set_xlabel('level ice thickness [m]')
    ax3.set_ylabel('deepest mode keel draft [m]')
    ax3.set_title(f'Deepest mode keel draft over LI deepest mode for {loc} in {year}')




    # change threshold for peaks intensity (haven't understood yet what and why)

    intensity_threshold = 0.2
    Dt = np.zeros(np.shape(draft_deeply_weekest_ridge))
    while True:
        # let the user change the threshold for the peaks intensity
        # change the threshold by numpad: 4 for decrease by 0.1, 6 for increase by 0.1, 2 for decrease by 0.01, 8 for increase by 0.01, 5 for exit
        print(f"Current intensity threshold is {intensity_threshold}. \nPress '4' for decrease by 0.1, '6' for increase by 0.1, '2' for decrease by 0.01, '8' for increase by 0.01, '5' to update the plot, '0' to exit the program. Press enter afterwards.")
        change = input()
        if change == '4':
            intensity_threshold -= 0.1
        elif change == '6':
            intensity_threshold += 0.1
        elif change == '2':
            intensity_threshold -= 0.01
        elif change == '8':
            intensity_threshold += 0.01
        elif change == '5':
            # update the peaks
            # makt to nan all values from peaks_location_filtered, that are either larger than 3 or that are at positions where peaks_intensity is smaller than intensity_threshold
            peaks_location_filtered = peaks_location.copy()
            for i in range(len(peaks_location_filtered)):
                peaks_location_filtered[i] = peaks_location_filtered[i][np.logical_or(peaks_location_filtered[i] > 3, peaks_intensity[i] < intensity_threshold)]
                # if there are no peaks left, set the maximum value of the peaks_location_filtered to Dt[i] = 0
                if len(peaks_location_filtered[i]) == 0:
                    Dt[i] = 0
                    color_array[i] = 'w'
                else:
                    Dt[i] = max(peaks_location_filtered[i])
                    color_array[i] = 'b'
            # set the x-values of scatter3 to Dt
            scatter3.set_offsets(np.c_[Dt, draft_deeply_weekest_ridge])
            # update the colors of the scatter3 according to the color_array
            scatter3.set_color(color_array)
        elif change == '0':
            break
        else:
            print("Invalid input. Please try again.")
            continue

    print("Bye!")
