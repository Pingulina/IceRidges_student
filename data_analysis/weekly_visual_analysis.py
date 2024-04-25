# analysing the restults of the ridge statistics function

import os
import numpy as np
import sys
import matplotlib.pyplot as plt
import json
import matplotlib.patches as mpatches
import scipy.stats

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


def weekly_visual_analysis():
    """
    """
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')
    while True:
        year = input("Enter the year you want to analyse: ")
        try:
            year = int(year)
        except ValueError:
            print("Wrong format. Please enter a valid year")
            continue
        
        
        path_to_json_processed = os.path.join(constants.pathName_data, 'ridge_statistics')
        json_file_name_processed = f"ridge_statistics_{year}.json"
        # check if the json file exists
        if not os.path.exists(os.path.join(path_to_json_processed, json_file_name_processed)):
            print(f"The json file {json_file_name_processed} does not exist. Please enter a valid year.")
            continue
        # load the ridge statistics from the json file
        with open(os.path.join(path_to_json_processed, json_file_name_processed), 'r') as file:
            dict_ridge_statistics = json.load(file)
            # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
            for loc in dict_ridge_statistics.keys():
                dict_ridge_statistics[loc] = j2d.jsonified2dict(dict_ridge_statistics[loc])

            
        
        locations_this_year = dict_ridge_statistics.keys() 
        loc = input("Enter the location you want to analyse: ")
        if loc in locations_this_year:
            break
        else:
            print(f"The location you entered is not in the data. Please enter a valid location. The locations for this year are: {locations_this_year}")
            continue
        
    # get the raw data for the year and location
    _, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json_mooring, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)
    
    
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

    for file in files:
        if file.split('_')[1] == 'statistics':
            with open(os.path.join(path_to_json_processed, file), 'r') as file:
                dict_ridge_statistics_year = json.load(file)
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
                for loc_year in dict_ridge_statistics_year.keys():
                    dict_ridge_statistics_year[loc_year] = j2d.jsonified2dict(dict_ridge_statistics_year[loc_year])
                    all_LIDM.extend(dict_ridge_statistics_year[loc_year]['level_ice_deepest_mode'])
                    all_MKD.extend(dict_ridge_statistics_year[loc_year]['mean_keel_draft']) 
                    all_Dmax.extend(dict_ridge_statistics_year[loc_year]['draft_weekly_deepest_ridge'])
                    all_number_of_ridges.extend(dict_ridge_statistics_year[loc_year]['number_ridges'])


    # plot the data
    week = 0
    plt.ion()
    figure_weekly_analysis = plt.figure(layout='constrained', figsize=(12,8)) # 4/5 aspect ratio
    gridspec_weekly_analysis = figure_weekly_analysis.add_gridspec(4,6)

    # figure ice data
    ax_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0:2,0:4])
    ax_ice_data.set_ylim(0, 30)
    ax_ice_data.set_ylabel('Draft [m]')
    # the x data is dateNum format, but the x labels should be the date in the format 'YYYY-MM-DD', every 50th day is labeled. DateNum has 24*3600 entries per day
    every_nth = 50
    dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]
    ax_ice_data.set_xticks(dateNum_every_day[::every_nth])
    ax_ice_data.set_xticklabels(date_time_stuff.datestr(dateNum_every_day[::every_nth], format='DD.MM.YY'))


    keel_draft_flat = [x for xs in dict_ridge_statistics[loc]['keel_draft_ridge'] for x in xs]
    keel_dateNum_flat = [x for xs in dict_ridge_statistics[loc]['keel_dateNum_ridge'] for x in xs]
    patch_current_week_ice_data = ax_ice_data.fill_between([dict_ridge_statistics[loc]['week_start'][week], dict_ridge_statistics[loc]['week_end'][week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)
    ULS_draft_signal = ax_ice_data.plot(dateNum, draft, color='tab:blue', label='Raw ULS draft signal', zorder=1)
    # RidgePeaks = ax_ice_data.scatter(dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['keel_draft'], color='red', label='Individual ridge peaks')
    RidgePeaks = ax_ice_data.scatter(keel_dateNum_flat, keel_draft_flat, color='red', label='Individual ridge peaks', s=0.75, zorder=2)
    # take the first element of each list in keel_dateNum and write it in keel_dateNum_weekStart
    keel_dateNum_weekStart = [date[0] for date in dict_ridge_statistics[loc]['keel_dateNum']]
    LI_thickness = ax_ice_data.step(keel_dateNum_weekStart, dict_ridge_statistics[loc]['level_ice_deepest_mode'], where='post', color='black', label='Level ice draft estimate', zorder=3)

    ax_ice_data.legend()

    # figure current week ice data

    ax_current_week_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,0:4])
    ax_current_week_ice_data.set_ylim(0, 30)
    ax_current_week_ice_data.set_ylabel('Draft [m]')
    ax_current_week_ice_data.set_xticks(dateNum_every_day[week*7:(week+1)*7])
    ax_current_week_ice_data.set_xticklabels(date_time_stuff.datestr(dateNum_every_day[week*7:(week+1)*7], format='DD.MM.YY'))
    
    ULS_draft_signal_thisWeek = ax_current_week_ice_data.plot(dict_ridge_statistics[loc]['keel_dateNum'][week], dict_ridge_statistics[loc]['keel_draft'][week], color='tab:blue', label='Raw ULS draft signal', zorder=0)
    RidgePeaks_thisWeek = ax_current_week_ice_data.scatter(dict_ridge_statistics[loc]['keel_dateNum_ridge'][week], dict_ridge_statistics[loc]['keel_draft_ridge'][week], color='red', label='Individual ridge peaks', zorder=1, s=2)
    LI_thickness_thisWeek = ax_current_week_ice_data.step(keel_dateNum_weekStart[week], dict_ridge_statistics[loc]['level_ice_deepest_mode'][week], where='post', color='green', label='Level ice draft estimate', zorder=2)

    # plot the results of this year and location and the results of all years and locations, to compare it
    # figure mean ridge keel depth
    ax_mean_ridge_keel_depth = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0,4:6])
    ax_mean_ridge_keel_depth.set_xlabel('Level ice deepest mode [m]')
    ax_mean_ridge_keel_depth.set_ylabel('Mean keel draft [m]')
    lrs1x = (max(all_LIDM)-min(all_LIDM))/20
    lrs1y = (max(all_MKD)-min(all_MKD))/20
    # all_LIDM = [dict_ridge_statistics[this_year][this_loc]['level_ice_deepest_mode'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    # all_MKD = [dict_ridge_statistics[this_year][this_loc]['mean_keel_draft'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    LI_mode_all = ax_mean_ridge_keel_depth.scatter(all_LIDM, all_MKD, color='tab:blue', label='keel depth', zorder=0, alpha=0.5)
    LI_mode_thisYear = ax_mean_ridge_keel_depth.scatter(dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['mean_keel_draft'], color='red', label='this year/location', zorder=1, s=4)
    # initialize rectangle to mark the current data point (week)
    CP1 = mpatches.Rectangle((dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]-lrs1x/2, dict_ridge_statistics[loc]['mean_keel_draft'][week]-lrs1y/2), lrs1x, lrs1y, edgecolor='k', facecolor='none')
    # add the patch to the axis
    ax_mean_ridge_keel_depth.add_patch(CP1)
    # initialize the text box to display level ice deepest mode and mean keel draft for the selected week
    # T1 = ax_mean_ridge_keel_depth.text(0.5, 0.5, f"LI DM = {0} || MKD = {0}", fontsize=12, transform=ax_mean_ridge_keel_depth.transAxes)


    # figure I don't know yet
    ax_kernel_estimate = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[1,4:6])
    draft_subset = draft[np.intersect1d(np.where(draft > 0), np.intersect1d(np.where(dateNum > dict_ridge_statistics[loc]['week_start'][week]), np.where(dateNum < dict_ridge_statistics[loc]['week_end'][week])))]
    # bw_sigma = np.std(draft_subset)
    # bw_n = len(draft_subset)
    # bw_h = 1.06*bw_sigma*bw_n**(-1/5)
    kde = scipy.stats.gaussian_kde(draft_subset)
    xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
    f = kde(xi)
    # ax_kernel_estimate.plot(xi, f, color='tab:blue', label='Kernel estimate', zorder=1)
    # plot level ice deepest mode
    DM_line = ax_kernel_estimate.plot([0, 0], [0, 6], color='tab:blue', label='deepest mode LI', zorder=1)
    AM_line = ax_kernel_estimate.plot([0, 0], [0, 6], color='red', label='average mode LI', ls='--', zorder=2)
    kernel_estimate_line = ax_kernel_estimate.plot(xi, f, color='tab:red', label='Kernel estimate', zorder=3)
    PS_line = ax_kernel_estimate.scatter(0, 0, color='k', zorder=3, label='peak signal', s=4)
    # histogram_line = ax_kernel_estimate.hist(draft_subset, bins=20, color='k', alpha=0.5, zorder=0, density=True)
    histogram_numpy = np.histogram(draft_subset, bins=20, density=True)
    histogram_line = ax_kernel_estimate.bar(histogram_numpy[1][:-1], histogram_numpy[0], align='edge', color='k', alpha=0.5, zorder=0, width=(max(draft_subset)-min(draft_subset))/20)
    # ax_kernel_estimate.legend()

    DM_line[0].set_xdata(dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'][week])
    AM_line[0].set_xdata(dict_ridge_statistics[loc]['level_ice_deepest_mode'][week])
    kernel_estimate_line[0].set_xdata(xi)
    kernel_estimate_line[0].set_ydata(f)
    PS_line.set_offsets([dict_ridge_statistics[loc]['peaks_location'][week], dict_ridge_statistics[loc]['peaks_intensity'][week]])
    

    # figure weekly deepest ridge
    ax_weekly_deepest_ridge = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2,4:6])
    ax_weekly_deepest_ridge.set_xlabel('Level ice deepest mode [m]')
    ax_weekly_deepest_ridge.set_ylabel('Max weekly draft [m]')
    lrs3x = (max(all_LIDM)-min(all_LIDM))/20
    lrs3y = (max(all_Dmax)-min(all_Dmax))/20
    # all_Dmax = [dict_ridge_statistics[this_year][this_loc]['draft_weekly_deepest_ridge'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    maxDrift_all = ax_weekly_deepest_ridge.scatter(all_LIDM, all_Dmax, color='tab:blue', label='max weekly draft', zorder=0, alpha=0.5)
    maxDrift_thisYear = ax_weekly_deepest_ridge.scatter(dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], color='red', label='this year/location', zorder=1, s=4)
    # initialize rectangle to mark the current data point (week)
    CP3 = mpatches.Rectangle((dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]-lrs3x/2, dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'][week]-lrs3y/2), lrs3x, lrs3y, edgecolor='k', facecolor='none')
    # add the patch to the axis
    ax_weekly_deepest_ridge.add_patch(CP3)
    # initialize the text box to display level ice deepest mode and mean keel draft for the selected week
    # T3 = ax_weekly_deepest_ridge.text(0.5, 0.5, f"LI DM = {0} || Dmax = {0}", fontsize=12, transform=ax_weekly_deepest_ridge.transAxes)

    # figure number of ridges
    ax_number_of_ridges = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[3,4:6])
    lrs4x = (max(all_LIDM)-min(all_LIDM))/20
    lrs4y = (max(all_number_of_ridges)-min(all_number_of_ridges))/20
    ax_number_of_ridges.set_xlabel('Level ice deepest mode [m]')
    ax_number_of_ridges.set_ylabel('Number of ridges')
    # all_number_of_ridges = [dict_ridge_statistics[this_year][this_loc]['number_ridges'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    number_of_ridges_all = ax_number_of_ridges.scatter(all_LIDM, all_number_of_ridges, color='tab:blue', label='number of ridges', zorder=0, alpha=0.5)
    number_of_ridges_thisYear = ax_number_of_ridges.scatter(dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['number_ridges'], color='red', label='this year/location', s=4, zorder=1)
    # initialize rectangle to mark the current data point (week)
    CP4 = mpatches.Rectangle((dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]-lrs4x/2, dict_ridge_statistics[loc]['number_ridges'][week]-lrs4y/2), lrs4x, lrs4y, edgecolor='k', facecolor='none')
    # add the patch to the axis
    ax_number_of_ridges.add_patch(CP4)
    # initialize the text box to display level ice deepest mode and mean keel draft for the selected week
    # T4 = ax_number_of_ridges.text(0.5, 0.5, f"LI DM = {0} || N = {0}", fontsize=12, transform=ax_number_of_ridges.transAxes)


    # loop through the weeks and update the plots
    # looping through the weeks is done by user input: user decides, if next week or previous week is displayed, this is done by pressing the 'f' key for forward and the 'd' key for backward
    
    while True:
        # update the week
        # get user input
        print("Press 'f' for forward and 'd' for backward and 'x' to exit the program. You can also enter the week number directly. In all cases, press enter afterwards.")
        user_input = input()
        if user_input == 'f':
            week += 1
        elif user_input == 'd':
            week -= 1
        elif user_input == 'x':
            break
        # if the week number is entered directly, set the week to the entered number
        elif user_input.isdigit():
            week = int(user_input)
        else:
            print("Invalid input.")
            continue

        if week < 0:
            # week is negative, set it to the last week
            week = len(dict_ridge_statistics[loc]['week_start'])-1
        elif week >= len(dict_ridge_statistics[loc]['week_start']):
            # week is too large, set it to the first week
            week = 0

        # update the plots
        # update the ice data plot
        patch_current_week_ice_data.remove()
        patch_current_week_ice_data = ax_ice_data.fill_between([dict_ridge_statistics[loc]['week_start'][week], dict_ridge_statistics[loc]['week_end'][week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)

        # update the current week ice data plot
        ax_current_week_ice_data.set_xticks(dateNum_every_day[week*7:(week+1)*7])
        ax_current_week_ice_data.set_xticklabels(date_time_stuff.datestr(dateNum_every_day[week*7:(week+1)*7], format='DD.MM.YY'))
        ax_current_week_ice_data.set_xlim(dateNum_every_day[week*7], dateNum_every_day[(week+1)*7])

        ULS_draft_signal_thisWeek[0].set_xdata(dict_ridge_statistics[loc]['keel_dateNum'][week])
        ULS_draft_signal_thisWeek[0].set_ydata(dict_ridge_statistics[loc]['keel_draft'][week])

        RidgePeaks_thisWeek.set_offsets(np.c_[dict_ridge_statistics[loc]['keel_dateNum_ridge'][week], dict_ridge_statistics[loc]['keel_draft_ridge'][week]])

        LI_thickness_thisWeek[0].set_xdata(keel_dateNum_weekStart[week])
        LI_thickness_thisWeek[0].set_ydata(dict_ridge_statistics[loc]['level_ice_deepest_mode'][week])

        # update the scatter plots

        # update the text boxes
        # T1.set_text(f"LI DM = {dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]} || MKD = {dict_ridge_statistics[loc]['mean_keel_draft'][week]}")
        # T3.set_text(f"LI DM = {dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]} || Dmax = {dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'][week]}")
        # T4.set_text(f"LI DM = {dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]} || N = {dict_ridge_statistics[loc]['number_ridges'][week]}")

        draft_subset = draft[np.intersect1d(np.where(draft > 0), np.intersect1d(np.where(dateNum > dict_ridge_statistics[loc]['week_start'][week]), np.where(dateNum < dict_ridge_statistics[loc]['week_end'][week])))]
        kde = scipy.stats.gaussian_kde(draft_subset)
        xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
        f = kde(xi)
        histogram_line.remove()
        histogram_numpy = np.histogram(draft_subset, bins=20, density=True)
        histogram_line = ax_kernel_estimate.bar(histogram_numpy[1][:-1], histogram_numpy[0], align='edge', color='k', alpha=0.5, zorder=0, width=(max(draft_subset)-min(draft_subset))/20)
        # histogram_line = ax_kernel_estimate.hist(draft_subset, bins=20, color='k', alpha=0.5, zorder=0, density=True)

        DM_line[0].set_xdata(dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'][week])
        AM_line[0].set_xdata(dict_ridge_statistics[loc]['level_ice_deepest_mode'][week])
        kernel_estimate_line[0].set_xdata(xi)
        kernel_estimate_line[0].set_ydata(f)
        PS_line.set_offsets([dict_ridge_statistics[loc]['peaks_location'][week], dict_ridge_statistics[loc]['peaks_intensity'][week]])

        # update the rectangle to mark the current data point (week)
        CP1.set_xy([dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]-lrs1x/2, dict_ridge_statistics[loc]['mean_keel_draft'][week]-lrs1y/2])
        CP3.set_xy([dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]-lrs3x/2, dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'][week]-lrs3y/2])
        CP4.set_xy([dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]-lrs4x/2, dict_ridge_statistics[loc]['number_ridges'][week]-lrs4y/2])


        # patch_current_week_ice_data.remove()
        # patch_current_week_ice_data = ax_ice_data.fill_between([dict_ridge_statistics[loc]['week_start'][week], dict_ridge_statistics[loc]['week_end'][week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)
        # # ULS_draft_signal_thisWeek.remove()
        # # remove the old data and plot the new data (plots and x labels)
        # ULS_draft_signal_thisWeek[0].remove()
        

        # ULS_draft_signal_thisWeek = ax_ice_data.plot(dict_ridge_statistics[loc]['keel_dateNum'][week], dict_ridge_statistics[loc]['keel_draft'][week], color='tab:blue', label='Raw ULS draft signal')
        # RidgePeaks_thisWeek.remove()
        # RidgePeaks_thisWeek = ax_ice_data.scatter(dict_ridge_statistics[loc]['keel_dateNum_ridge'][week], dict_ridge_statistics[loc]['keel_draft_ridge'][week], color='red', label='Individual ridge peaks')
        # LI_thickness_thisWeek.remove()
        # LI_thickness_thisWeek = ax_ice_data.step(dict_ridge_statistics[loc]['keel_dateNum'][week], dict_ridge_statistics[loc]['level_ice_deepest_mode'][week], where='mid', color='green', label='Level ice draft estimate')
        # LI_mode_thisYear.remove()
        # LI_mode_thisYear = ax_mean_ridge_keel_depth.scatter(dict_ridge_statistics[loc]['level_ice_deepest_mode'][week], dict_ridge_statistics[loc]['mean_keel_draft'][week], color='red', label='this year/location')
        # T1.remove()
        # T1 = ax_mean_ridge_keel_depth.text(0.5, 0.5, f"LI DM = {dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]} || MKD = {dict_ridge_statistics[loc]['mean_keel_draft'][week]}", fontsize=12, transform=ax_mean_ridge_keel_depth.transAxes)

        # maxDrift_thisYear.remove()
        # maxDrift_thisYear = ax_weekly_deepest_ridge.scatter(dict_ridge_statistics[loc]['level_ice_deepest_mode'][week], dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'][week], color='red', label='this year/location')
        # T3.remove()
        # T3 = ax_weekly_deepest_ridge.text(0.5, 0.5, f"LI DM = {dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]} || Dmax = {dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'][week]}", fontsize=12, transform=ax_weekly_deepest_ridge.transAxes)

        # number_of_ridges_thisYear.remove()
        # number_of_ridges_thisYear = ax_number_of_ridges.scatter(dict_ridge_statistics[loc]['level_ice_deepest_mode'][week], dict_ridge_statistics[loc]['number_ridges'][week], color='red', label='this year/location')
        # T4.remove()
        # T4 = ax_number_of_ridges.text(0.5, 0.5, f"LI DM = {dict_ridge_statistics[loc]['level_ice_deepest_mode'][week]} || N = {dict_ridge_statistics[loc]['number_ridges'][week]}", fontsize=12, transform=ax_number_of_ridges.transAxes)

        figure_weekly_analysis.canvas.draw()

    print("Program exited. Goodbye.")
    return None