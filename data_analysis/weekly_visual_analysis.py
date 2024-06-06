# analysing the restults of the ridge statistics function

import os
import numpy as np
import sys
import matplotlib.pyplot as plt
import json
import matplotlib.patches as mpatches
import scipy.stats
from copy import deepcopy

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
constants = import_module('constants', 'helper_functions')
j2d = import_module('jsonified2dict', 'initialization_preparation')
date_time_stuff = import_module('date_time_stuff', 'helper_functions')
load_data = import_module('load_data', 'data_handling')
data_analysis_plot = import_module('data_analysis_plot', 'plot_functions')
user_input_interaction = import_module('user_input_iteration', 'user_interaction')


def weekly_visual_analysis():
    """
    """
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    dateNum, draft, dict_ridge_statistics, year, loc = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, path_to_json_mooring=path_to_json_mooring
                                                                        )
    
    
    # get the data for all years and locations each in an array
    # in Data_results/ridge_statistics/ridge_statistics_{year}.json the data is stored in the following format:
    # dict_ridge_statistics = {loc1: {'data_name' : data, 'data_name' : data, ... }, loc2: {'data_name' : data, 'data_name' : data, ...}, ...}

    # list all files in the directory
    files = os.listdir(path_to_json_processed)
    # sort the files by year
    files.sort()

    all_LIDM = []
    all_MKD = []
    all_Dmax = []
    all_number_of_ridges = []

    dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
    for year in dict_ridge_statistics_year_all.keys():
        # dict_ridge_statistics_year = dict_ridge_statistics_year_all[year]
        for loc_year in dict_ridge_statistics_year_all[year].keys():
            all_LIDM.extend(deepcopy(dict_ridge_statistics_year_all[year][loc_year]['level_ice_deepest_mode']))
            all_MKD.extend(deepcopy(dict_ridge_statistics_year_all[year][loc_year]['mean_keel_draft']) )
            all_Dmax.extend(deepcopy(dict_ridge_statistics_year_all[year][loc_year]['draft_weekly_deepest_ridge']))
            all_number_of_ridges.extend(deepcopy(dict_ridge_statistics_year_all[year][loc_year]['number_ridges']))


    # plot the data
    week = 0
    plt.ion()
    figure_weekly_analysis = plt.figure(layout='constrained', figsize=(12,8)) # 4/5 aspect ratio
    gridspec_weekly_analysis = figure_weekly_analysis.add_gridspec(4,6)
    
    every_nth = 50
    dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]
    xTickLabels = date_time_stuff.datestr(dateNum_every_day, format='DD.MM.YY')

    # figure ice data
    ax_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0:2,0:4])

    ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness = data_analysis_plot.initialize_plot_data_draft(
        ax_ice_data, dateNum, draft, dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
        dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['week_start'], 
        dict_ridge_statistics[loc]['week_end'], week, every_nth, 'Date', 'Draft [m]', [0, 30], xTickLabels=xTickLabels)
    
    ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness = data_analysis_plot.plot_data_draft(
        ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness, dateNum, draft, dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
        dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['week_start'], 
        dict_ridge_statistics[loc]['week_end'], week, every_nth, xTickLabels, [0, 30])
    
    
    # figure current week ice data

    ax_current_week_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,0:4])

    ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.initialize_plot_weekly_data_draft(
        ax_current_week_ice_data, dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['keel_draft'], dict_ridge_statistics[loc]['keel_dateNum_ridge'], 
        dict_ridge_statistics[loc]['keel_draft_ridge'], dict_ridge_statistics[loc]['keel_dateNum'], 
        dict_ridge_statistics[loc]['level_ice_deepest_mode'], week, 'Date', 'Draft [m]', [0, 30], xTickLabels=xTickLabels)
    

    ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.plot_weekly_data_draft(
        ax_current_week_ice_data,  ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['keel_draft'], 
        dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], dict_ridge_statistics[loc]['keel_dateNum'], 
        dict_ridge_statistics[loc]['level_ice_deepest_mode'], dateNum_every_day, week, xTickLabels, [0, 30])
    
    # plot the results of this year and location and the results of all years and locations, to compare it
    # figure mean ridge keel depth
    ax_mean_ridge_keel_depth = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0,4:6])

    ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1 = data_analysis_plot.initialize_plot_weekly_data_scatter(
        ax_mean_ridge_keel_depth, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['mean_keel_draft'], 
        week, 'Level ice deepest mode [m]', 'Mean keel draft [m]')

    ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1 = data_analysis_plot.plot_weekly_data_scatter(
        ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['mean_keel_draft'], 
        week)

    # figure I don't know yet
    ax_kernel_estimate = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[1,4:6])
    ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.initialize_plot_needName(
        ax_kernel_estimate, dateNum, draft, dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week, 
        dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
        dict_ridge_statistics[loc]['peaks_location'], dict_ridge_statistics[loc]['peaks_intensity'])
    ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.plot_needName(
        ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line, dateNum, draft, dict_ridge_statistics[loc]['week_start'], 
        dict_ridge_statistics[loc]['week_end'], week, dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], 
        dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['peaks_location'], dict_ridge_statistics[loc]['peaks_intensity'])

    # figure weekly deepest ridge
    ax_weekly_deepest_ridge = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2,4:6])
    ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3 = data_analysis_plot.initialize_plot_weekly_data_scatter(
        ax_weekly_deepest_ridge, all_LIDM, all_Dmax, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], 
        week, 'Level ice deepest mode [m]', 'Max weekly draft [m]')
    ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3 = data_analysis_plot.plot_weekly_data_scatter(
        ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3, all_LIDM, all_Dmax, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], 
        week)

    # figure number of ridges
    ax_number_of_ridges = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[3,4:6])
    ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4 = data_analysis_plot.initialize_plot_weekly_data_scatter(
        ax_number_of_ridges, all_LIDM, all_number_of_ridges, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['number_ridges'], 
        week, 'Level ice deepest mode [m]', 'Number of ridges')
    ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4 = data_analysis_plot.plot_weekly_data_scatter(
        ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4, all_LIDM, all_number_of_ridges, 
        dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['number_ridges'], week)

    # loop through the weeks and update the plots
    # looping through the weeks is done by user input: user decides, if next week or previous week is displayed, this is done by pressing the 'f' key for forward and the 'd' key for backward
    
    while True:
        # update the week
        # get user input
        print("Press 'f' for forward and 's' for backward and 'x' to exit the program. You can also enter the week number directly. In all cases, press enter afterwards.")
        success, week = user_input_interaction.get_user_input_iteration(week, len(dict_ridge_statistics[loc]['week_start']))
        if success == -1:
            break
        elif success == 0:
            continue
        elif success == 1:
            pass
        else:
            raise ValueError("Invalid success value.")

        
        # user_input = input()
        # if user_input == 'f':
        #     week += 1
        # elif user_input == 'd':
        #     week -= 1
        # elif user_input == 'x':
        #     break
        # # if the week number is entered directly, set the week to the entered number
        # elif user_input.isdigit():
        #     week = int(user_input)
        # else:
        #     print("Invalid input.")
        #     continue

        # if week < 0:
        #     # week is negative, set it to the last week
        #     week = len(dict_ridge_statistics[loc]['week_start'])-1
        # elif week >= len(dict_ridge_statistics[loc]['week_start']):
        #     # week is too large, set it to the first week
        #     week = 0

        # update the plots
        # update the ice data plot
        ax_ice_data, patch_current_week_ice_data = data_analysis_plot.update_plot_data_draft(
            ax_ice_data, patch_current_week_ice_data, draft, dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week)
        # patch_current_week_ice_data.remove()
        # patch_current_week_ice_data = ax_ice_data.fill_between([dict_ridge_statistics[loc]['week_start'][week], dict_ridge_statistics[loc]['week_end'][week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)

        # update the current week ice data plot
        data_analysis_plot.update_plot_weekly_data_draft(
            ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, dict_ridge_statistics[loc]['keel_dateNum'], 
            dict_ridge_statistics[loc]['keel_draft'], dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
            dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dateNum_every_day, week, xTickLabels)

        ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.update_plot_needName(
            ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line, dateNum, draft, dict_ridge_statistics[loc]['week_start'], 
            dict_ridge_statistics[loc]['week_end'], week, dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
            dict_ridge_statistics[loc]['peaks_location'], dict_ridge_statistics[loc]['peaks_intensity'])

        # update the rectangle to mark the current data point (week)
        ax_mean_ridge_keel_depth, CP1 = data_analysis_plot.update_plot_weekly_data_scatter(
            ax_mean_ridge_keel_depth, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
            dict_ridge_statistics[loc]['mean_keel_draft'], week, CP1)
        
        ax_weekly_deepest_ridge, CP3 = data_analysis_plot.update_plot_weekly_data_scatter(
            ax_weekly_deepest_ridge, all_LIDM, all_Dmax, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
            dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], week, CP3)
        
        ax_number_of_ridges, CP4 = data_analysis_plot.update_plot_weekly_data_scatter(
            ax_number_of_ridges, all_LIDM, all_number_of_ridges, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
            dict_ridge_statistics[loc]['number_ridges'], week, CP4)
        
        figure_weekly_analysis.canvas.draw()

    print("Program exited. Goodbye.")
    return None