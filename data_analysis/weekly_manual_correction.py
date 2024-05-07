### description from Matlab
# This script is used to analyse the level ice draft identification point by point. First, year and
# location is specified of the mooring subset to be analysed. Analysis is done by observing several figures.

# Figure 1 illustrates a whole year of draft data suplemented with level ice draft and identified keels.

# Figure 2 zoomed in section of the current week's data.

# Figure 3 has four subplots showing the following :
# SP1 : LI DM vs Mean ridge keel draft
# SP2 : Draft histogram, PDF, AM, DM
# SP3 : LI DM vs Weekly deepest ridge draft
# SP4: LI DM vs Number of ridges

# Figure 4 shows the "distogram" plot where evolution of the level ice can be seen and outliers can
# be identified more reliably

# INSTRUCTIONS FOR GOING THROUGH THE LOOP
# 
#     - Arrow right     -   Go one week forward
#     - Arrow left      -   Go one week back
#     - Arrow up        -   Go 5 weeks forward
#     - Arrow down      -   Go 5 weeks back
#     - NumPad 0        -   Select the point to be analysed in Figure 4 (only horisontal location is enogh)
#     - Enter           -   Correct the location of level ice thickness in Figure 3
#     - NumPad -        -   Delete current point
#     - Esc             -   Go forward to next season/location

# In order to close the loop completely do the following
#       First press "NumPad +" and then press "Esc"

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import json
from copy import deepcopy
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
constants = import_module('constants', 'helper_functions')
load_data = import_module('load_data', 'data_handling')
date_time_stuff = import_module('date_time_stuff', 'helper_functions')
data_analysis_plot = import_module('data_analysis_plot', 'data_analysis')
user_input_iteration = import_module('user_input_iteration', 'user_interaction')

def weekly_manual_correction(number_ridges_threshold=15):
    """correct the data manually
    :input: number_ridges_threshold: int: minimal number of ridges per dataset
    """

    # load the data
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    dateNum, draft, dict_ridge_statistics, year_user, loc_user = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, path_to_json_mooring=path_to_json_mooring
                                                                        )
    
    
    # get the data for all years and locations each in an array
    # in Data_results/ridge_statistics/ridge_statistics_{year}.json the data is stored in the following format:
    # dict_ridge_statistics = {loc1: {'data_name' : data, 'data_name' : data, ... }, loc2: {'data_name' : data, 'data_name' : data, ...}, ...}

    # list all files in the directory
    files = os.listdir(path_to_json_processed)
    # sort the files by year
    files.sort()

    dict_ridge_statistics_year_all = {}

    # load the data from mooring_locations.json to get the locations for all years
    with open(os.path.join(constants.pathName_dataRaw, 'mooring_locations.json'), 'r') as file:
        dict_mooring_locations = json.load(file)
    # get the years from the files   
    mooring_years = [thisFile.split('.')[0].split('_')[-1] for thisFile in files]
    # kick out all the years from dict_mooring_locations, that are not stored in the ridge_statistics folder
    dict_mooring_locations = {key: dict_mooring_locations[key] for key in dict_mooring_locations.keys() if key[0:4] in mooring_years}

    # dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)

    # # for every year and location, get the number of ridges. If there are less than number_ridges_threshold ridges, delete the data
    # for year in dict_ridge_statistics_year_all.keys():
    #     for loc in dict_ridge_statistics_year_all[year].keys():
    #         if len(dict_ridge_statistics_year_all[year][loc]['number_ridges']) < number_ridges_threshold:
    #             del dict_ridge_statistics_year_all[year][loc]

    # get the data for all years and locations each in an array
    all_LIDM = []
    all_MKD = []
    all_Dmax = []
    all_number_of_ridges = []

    dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
    for year in dict_ridge_statistics_year_all.keys():
        dict_ridge_statistics_year = dict_ridge_statistics_year_all[year]
        for loc_year in dict_ridge_statistics_year.keys():
            all_LIDM.extend(dict_ridge_statistics_year[loc_year]['level_ice_deepest_mode'])
            all_MKD.extend(dict_ridge_statistics_year[loc_year]['mean_keel_draft']) 
            all_Dmax.extend(dict_ridge_statistics_year[loc_year]['draft_weekly_deepest_ridge'])
            all_number_of_ridges.extend(dict_ridge_statistics_year[loc_year]['number_ridges'])

    # iterate over all years and locations
    season_list = list(dict_mooring_locations.keys())
    season_index = 0
    while True:
        print(f"--- Season {season_list[season_index]}---")
        print("Press 'f' for next season, 'd' for this season and 's' for last season and 'x' to exit the program. You can also enter the season_index directly. In all cases, press enter afterwards.")
        success, season_index = user_input_iteration.get_user_input_iteration(season_index, len(season_list))
        if success == -1:
            break
        elif success == 0:
            continue
        elif success == 1:
            pass
        else:
            raise ValueError("Invalid success value.")
        
        season = season_list[season_index]

    
        loc_list = list(dict_mooring_locations[season].keys())
        loc_index = 0
        while True:
            print("--- Location ---")
            print("Press 'f' for next location, 'd' for this location and 's' for last location. Press 'x' to exit this season. You can also enter the loc_index directly. In all cases, press enter afterwards.")
            success, loc_index = user_input_iteration.get_user_input_iteration(loc_index, len(loc_list))
            if success == -1:
                break
            elif success == 0:
                continue
            elif success == 1:
                pass
            else:
                raise ValueError("Invalid success value.")
            
            loc = loc_list[loc_index]
        
            if len(season.split('-')) > 1:
                year = season.split('-')[0]
                year = int(year) # get the year as integer
            # get the data for the year and location
            dateNum, draft, dict_ridge_statistics, _, _ = load_data.load_data_oneYear(year, loc, path_to_json_processed, path_to_json_mooring)
            
            # get the number of ridges
            number_ridges = dict_ridge_statistics[loc]['number_ridges']
            # get the indices of ridges that have less than number_ridges_threshold ridges	
            number_ridges_delete = np.where([ridgeNum < number_ridges_threshold for ridgeNum in dict_ridge_statistics[loc]['number_ridges']])
            # if the number of ridges is less than the threshold, delete the data
            for key in dict_ridge_statistics[loc].keys():
                dict_ridge_statistics[loc][key] = remove_indices(dict_ridge_statistics[loc][key], number_ridges_delete)

            dict_ridge_statistics_year_all[year][loc] = deepcopy(dict_ridge_statistics[loc])

            # make weekly histogram data that are later used for creating the distogram plot
            period = (24//constants.level_ice_time)*constants.level_ice_statistic_days # hours per sampling unit (week)
            histBins = np.arange(-0.1, 8+0.1, 0.1)

            # instantaneaous LI draft estimated by finding the mode of the distribution. 
            # Multiplication with 1000, finding the mode and subsequent division by 1000 s done because the mode function bins the data in integers. 
            # dateNum_LI is the time of the instantaneous estimates

            dt = np.round(np.mean(np.diff(dateNum))*3600*24)
            mean_time = 3600 * constants.level_ice_time
            mean_points = mean_time / dt
            numberElements = int(np.floor(len(dateNum)/mean_points) * mean_points)
            dateNum_reshape = dateNum[:numberElements]
            dateNum_reshape = dateNum_reshape.reshape(int(len(dateNum)/mean_points), int(mean_points))
            draft_reshape = draft[:numberElements]
            draft_reshape = draft_reshape.reshape(int(len(draft)/mean_points), int(mean_points))

            hi = compute_mode(np.array(np.round(np.array(draft_reshape)*1000, 0))) / 1000
            hi_1 = scipy.stats.mode(np.round(np.array(draft_reshape)*1000, 0), axis=1).mode / 1000
            # max(dict_ridge_statistics[loc]['keel_draft'], key=dict_ridge_statistics[loc]['keel_draft'].count)
            # dateNum_LI = dict_ridge_statistics[loc]['keel_dateNum'][dict_ridge_statistics[loc]['keel_draft'].index(hi)]
            dateNum_LI = np.mean(dateNum_reshape, axis=1)

            # numberElements = len(hi)//period
            # number_weeks = int(np.floor(numberElements * (1/(3600/dt)) / 168))
            HHi = [[]] * (len(hi)//period )
            dateNum_hist = [[]] * (len(hi)//period )

            for i, n in enumerate(range(0,len(hi)-period,period)):
                # interpolate hi[i*period:(i+1)*period] to get the values for the points histBins
                HHi[i], _ = np.histogram(hi[n:n+period], bins=histBins) #  HHi[i] = np.digitize(hi[n:n+period], histBins) # equivalent to histcounts in matlab, returns the indices of the bins to which each value in input array belongs.
                dateNum_hist[i] = np.mean(dateNum_LI[n:n+period])
            HHi = np.array(HHi)
            hh = histBins[0:-1]+np.diff(histBins)/2
            [X, Y] = np.meshgrid(dateNum_hist, hh)
            # plot the data
            # the figure should contain a spectogram and some lines on top of it (all in one plot)
            HHi_plot = HHi / (period+1)
            
            
            # plot the data

            week = 0
            plt.ion()
            figure_weekly_analysis = plt.figure(layout='constrained', figsize=(12,8)) # 4/5 aspect ratio
            # set the title of the figure
            figure_weekly_analysis.suptitle(f"Season {season}, location {loc}, week {week}", fontsize=16)
            gridspec_weekly_analysis = figure_weekly_analysis.add_gridspec(4,6)
            
            every_nth = 50
            dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]
            xTickLabels = date_time_stuff.datestr(dateNum_every_day, format='DD.MM.YY')

            # figure ice data
            ax_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0:2,0:4])
            
            ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness = data_analysis_plot.plot_data_draft(
                ax_ice_data, dateNum, draft, dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
                dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['week_start'], 
                dict_ridge_statistics[loc]['week_end'], week, every_nth, xTickLabels, 'Date', 'Draft [m]', [0, 30])

            # figure current week ice data

            ax_current_week_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,0:2])
            ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.plot_weekly_data_draft(
                ax_current_week_ice_data, dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['keel_draft'], dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], dict_ridge_statistics[loc]['keel_dateNum'], 
                dict_ridge_statistics[loc]['level_ice_deepest_mode'], dateNum_every_day, week, xTickLabels, 'Date', 'Draft [m]', [0, 30], dateTickDistance=2)
            

            ax_specto = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,2:4])
            ax_specto, thisWeek_patch_specto, scatter_DM, scatter_AM, CP44 = data_analysis_plot.plot_spectrum(
                ax_specto, X, Y, HHi_plot, draft, dict_ridge_statistics[loc]['mean_dateNum'], dateNum_LI, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week)

            # plot the results of this year and location and the results of all years and locations, to compare it
            # figure mean ridge keel depth
            ax_mean_ridge_keel_depth = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0,4:6])

            ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1 = data_analysis_plot.plot_weekly_data_scatter(
                ax_mean_ridge_keel_depth, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['mean_keel_draft'], 
                week, loc, 'Level ice deepest mode [m]', 'Mean keel draft [m]')

            # figure I don't know yet
            ax_kernel_estimate = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[1,4:6])

            ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.plot_needName(
                ax_kernel_estimate, dateNum, draft, dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week, 
                dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['peaks_location'], dict_ridge_statistics[loc]['peaks_intensity'])

            # figure weekly deepest ridge
            ax_weekly_deepest_ridge = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2,4:6])

            ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3 = data_analysis_plot.plot_weekly_data_scatter(
                ax_weekly_deepest_ridge, all_LIDM, all_Dmax, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], 
                week, loc, 'Level ice deepest mode [m]', 'Max weekly draft [m]')

            # figure number of ridges
            ax_number_of_ridges = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[3,4:6])

            ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4 = data_analysis_plot.plot_weekly_data_scatter(
                ax_number_of_ridges, all_LIDM, all_number_of_ridges, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['number_ridges'], 
                week, loc, 'Level ice deepest mode [m]', 'Number of ridges')
            
           
            ### manual correction
            print("--- weekly manual correction ---")
            while True:
                # update the week
                # get user input
                print(f"Press 'f' for next week and 's' for last week. Press 'x' to finish this location. You can also enter the week number directly. In all cases, press enter afterwards.")
                success, week = user_input_iteration.get_user_input_iteration(week, len(dict_ridge_statistics[loc]['week_start']))
                if success == -1:
                    break
                elif success == 0:
                    continue
                elif success == 1:
                    pass
                else:
                    raise ValueError("Invalid success value.")

                # update the plots
                figure_weekly_analysis.suptitle(f"Season {season}, location {loc}, week {week}", fontsize=16)
                # update the ice data plot
                ax_ice_data, patch_current_week_ice_data = data_analysis_plot.update_plot_data_draft(
                    ax_ice_data, patch_current_week_ice_data, draft, dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week)

                # update the current week ice data plot
                ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.update_plot_weekly_data_draft(
                    ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, dict_ridge_statistics[loc]['keel_dateNum'], 
                    dict_ridge_statistics[loc]['keel_draft'], dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
                    dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dateNum_every_day, week, xTickLabels)
                
                ax_specto, CP44 = data_analysis_plot.update_plot_spectrum(
                    ax_specto, CP44, dict_ridge_statistics[loc]['mean_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], week)

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


def remove_indices(d_at_key, indices):
    """Remove elements at specific indices from all lists or numpy arrays in a dictionary entry.
    :param d: dictionary to modify
    :type d_at_key: dict entry
    :param indices: indices of elements to remove
    :type indices: list
    :return: dictionary with elements removed
    :rtype: dict
    """
    if isinstance(indices, tuple):
        indices = indices[0] # get the indices from the tuple

    if isinstance(d_at_key, list):
        d_at_key = [x for j, x in enumerate(d_at_key) if j not in indices]
    elif isinstance(d_at_key, np.ndarray):
        d_at_key = np.delete(d_at_key, indices)
    else:
        raise ValueError("The input data type is not supported. Please use a list or a numpy array.")
    return d_at_key


def compute_mode(data):
    """Compute the mode of the data
    :param data: list or numpy array
    :return: mode of the data
    """
    # if data is 2d, make it for every row
    if len(data.shape) > 1:
        mode = np.zeros(data.shape[0])
        for i in range(data.shape[0]):
            mode[i] =  compute_mode(data[i])
    else:
        # X = np.sort(data)   # sort the data
        # indices = np.where(np.diff(np.concatenate((X, [np.inf])))  > 0)[0] # indices where repeated values change
        # i = np.argmax(np.diff(np.concatenate(([0], indices))))     # longest persistence length of repeated values
        # mode = X[indices[i]]
        data_frequency_values, data_frequency = to_frequency(data)
        mode = data_frequency_values[np.argmax(data_frequency)]

    return mode


def to_frequency(data: np.ndarray):
    """Convert data from time to frequency domain
    :param data: numpy array, data in time domain
    :return: numpy array, data values in frequency domain
    :return: numpy array, data in frequency domain
    """
    # sort the data
    X = np.sort(data)
    # count how often values occur
    indices = np.where(np.diff(np.concatenate((X, np.ones(np.shape(X)[0]) * np.inf)))  > 0)[0] # indices where repeated values change
    data_frequency_values = data[indices] # all different values
    # count how often each value occurs (difference between the indices)
    data_frequency = np.diff(np.concatenate((indices, np.ones(1)*len(data)))) # number of occurences of each value

    return data_frequency_values, data_frequency
