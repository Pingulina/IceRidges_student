# analysing the restults of the ridge statistics function

import os
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

    # plot the results of this year and location and the results of all years and locations, to compare it
    # figure mean ridge keel depth
    ax_mean_ridge_keel_depth = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0,1])
    all_LIDM = [dict_ridge_statistics[this_year][this_loc]['level_ice_deepest_mode'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    all_MKD = [dict_ridge_statistics[this_year][this_loc]['mean_keel_draft'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    LI_mode_all = ax_mean_ridge_keel_depth.scatter(all_LIDM, all_MKD, color='blue', label='keel depth')
    LI_mode_thisYear = ax_mean_ridge_keel_depth.scatter(dict_ridge_statistics[year][loc]['level_ice_deepest_mode'], dict_ridge_statistics[year][loc]['mean_keel_draft'], color='red', label='this year/location')
    # initialize rectangle to mark the current data point (week)
    CP1 = mpatches.Rectangle((0,0), 0.2, 0.2, color='k', alpha=0.5)
    # initialize the text box to display level ice deepest mode and mean keel draft for the selected week
    T1 = ax_mean_ridge_keel_depth.text(0.5, 0.5, f"LI DM = {0} || MKD = {0}", fontsize=12, transform=ax_mean_ridge_keel_depth.transAxes)


    # figure I don't know yet
    ax_ = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[1,1])

    # figure weekly deepest ridge
    ax_weekly_deepest_ridge = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2,1])
    all_Dmax = [dict_ridge_statistics[this_year][this_loc]['draft_weekly_deepest_ridge'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    maxDrift_all = ax_weekly_deepest_ridge.scatter(all_LIDM, all_Dmax, color='blue', label='max weekly draft')
    maxDrift_thisYear = ax_weekly_deepest_ridge.scatter(dict_ridge_statistics[year][loc]['level_ice_deepest_mode'], dict_ridge_statistics[year][loc]['draft_weekly_deepest_ridge'], color='red', label='this year/location')
    # initialize rectangle to mark the current data point (week)
    CP3 = mpatches.Rectangle((0,0), 0.2, 0.2, color='k', alpha=0.5)
    # initialize the text box to display level ice deepest mode and mean keel draft for the selected week
    T3 = ax_weekly_deepest_ridge.text(0.5, 0.5, f"LI DM = {0} || Dmax = {0}", fontsize=12, transform=ax_weekly_deepest_ridge.transAxes)

    # figure number of ridges
    ax_number_of_ridges = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[3,1])
    all_number_of_ridges = [dict_ridge_statistics[this_year][this_loc]['number_of_ridges'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    number_of_ridges_all = ax_number_of_ridges.scatter(all_LIDM, all_number_of_ridges, color='blue', label='number of ridges')
    number_of_ridges_thisYear = ax_number_of_ridges.scatter(dict_ridge_statistics[year][loc]['level_ice_deepest_mode'], dict_ridge_statistics[year][loc]['number_of_ridges'], color='red', label='this year/location')
    # initialize rectangle to mark the current data point (week)
    CP4 = mpatches.Rectangle((0,0), 0.2, 0.2, color='k', alpha=0.5)
    # initialize the text box to display level ice deepest mode and mean keel draft for the selected week
    T4 = ax_number_of_ridges.text(0.5, 0.5, f"LI DM = {0} || N = {0}", fontsize=12, transform=ax_number_of_ridges.transAxes)


    # loop through the weeks and update the plots
    # looping through the weeks is done by user input: user decides, if next week or previous week is displayed, this is done by pressing the 'f' key for forward and the 'd' key for backward
    week = 0
    while True:
        # update the plots
        patch_current_week_ice_data.remove()
        patch_current_week_ice_data = ax_ice_data.fill_between(dateNum, 0, draft, color='lightblue', label='Current week ice data')
        RidgePeaks_thisWeek.remove()
        RidgePeaks_thisWeek = ax_ice_data.scatter(dict_ridge_statistics[year][loc]['keel_dateNum'][week], dict_ridge_statistics[year][loc]['keel_draft'][week], color='red', label='Individual ridge peaks')
        LI_thickness_thisWeek.remove()
        LI_thickness_thisWeek = ax_ice_data.step(dict_ridge_statistics[year][loc]['keel_dateNum'][week], dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week], where='mid', color='green', label='Level ice draft estimate')
        LI_mode_thisYear.remove()
        LI_mode_thisYear = ax_mean_ridge_keel_depth.scatter(dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week], dict_ridge_statistics[year][loc]['mean_keel_draft'][week], color='red', label='this year/location')
        T1.remove()
        T1 = ax_mean_ridge_keel_depth.text(0.5, 0.5, f"LI DM = {dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week]} || MKD = {dict_ridge_statistics[year][loc]['mean_keel_draft'][week]}", fontsize=12, transform=ax_mean_ridge_keel_depth.transAxes)

        maxDrift_thisYear.remove()
        maxDrift_thisYear = ax_weekly_deepest_ridge.scatter(dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week], dict_ridge_statistics[year][loc]['draft_weekly_deepest_ridge'][week], color='red', label='this year/location')
        T3.remove()
        T3 = ax_weekly_deepest_ridge.text(0.5, 0.5, f"LI DM = {dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week]} || Dmax = {dict_ridge_statistics[year][loc]['draft_weekly_deepest_ridge'][week]}", fontsize=12, transform=ax_weekly_deepest_ridge.transAxes)

        number_of_ridges_thisYear.remove()
        number_of_ridges_thisYear = ax_number_of_ridges.scatter(dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week], dict_ridge_statistics[year][loc]['number_of_ridges'][week], color='red', label='this year/location')
        T4.remove()
        T4 = ax_number_of_ridges.text(0.5, 0.5, f"LI DM = {dict_ridge_statistics[year][loc]['level_ice_deepest_mode'][week]} || N = {dict_ridge_statistics[year][loc]['number_of_ridges'][week]}", fontsize=12, transform=ax_number_of_ridges.transAxes)

        # update the week
        # get user input
        print("Press 'f' for forward and 'd' for backward and x to exit the program.")
        user_input = input()
        if user_input == 'f':
            week += 1
            continue
        elif user_input == 'd':
            week -= 1
            continue
        elif user_input == 'x':
            break

    print("Program exited. Goodbye.")
    return None