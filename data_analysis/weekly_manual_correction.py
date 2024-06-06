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
data_analysis_plot = import_module('data_analysis_plot', 'plot_functions')
user_input_iteration = import_module('user_input_iteration', 'user_interaction')
dict2json = import_module('dict2json', 'data_handling')


def weekly_manual_correction(number_ridges_threshold=15):
    """correct the data manually
    :input: number_ridges_threshold: int: minimal number of ridges per dataset
    """

    # load the data
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    path_to_json_corrected = os.path.join(constants.pathName_dataResults, 'ridge_statistics_corrected')
    dateNum, draft, _, year_user, loc_user = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, 
                                                                         path_to_json_mooring=path_to_json_mooring, load_dict_ridge_statistics=False
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
    mooring_years = [thisFile.split('.')[0].split('_')[-1][0:4] for thisFile in files]
    
    # kick out all the years from dict_mooring_locations, that are not stored in the ridge_statistics folder
    dict_mooring_locations = {key: dict_mooring_locations[key] for key in dict_mooring_locations.keys() if key[0:4] in mooring_years}

    # dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)

    # # for every year and location, get the number of ridges. If there are less than number_ridges_threshold ridges, delete the data
    # for year in dict_ridge_statistics_year_all.keys():
    #     for loc in dict_ridge_statistics_year_all[year].keys():
    #         if len(dict_ridge_statistics_year_all[year][loc]['number_ridges']) < number_ridges_threshold:
    #             del dict_ridge_statistics_year_all[year][loc]

    # get the data for all years and locations each in an array
    # all_LIDM = []
    # all_MKD = []
    # all_Dmax = []
    # all_number_of_ridges = []

    dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)
                # make all entries in data to the data format named in type (e.g. list, dict, str, np.ndarray, np.float, ...)
    # for year in dict_ridge_statistics_year_all.keys():
    #     dict_ridge_statistics_year = dict_ridge_statistics_year_all[year]
    #     for loc_year in dict_ridge_statistics_year.keys():
    #         all_LIDM.extend(deepcopy(dict_ridge_statistics_year[loc_year]['level_ice_deepest_mode']))
    #         all_MKD.extend(deepcopy(dict_ridge_statistics_year[loc_year]['mean_keel_draft']))
    #         all_Dmax.extend(deepcopy(dict_ridge_statistics_year[loc_year]['draft_weekly_deepest_ridge']))
    #         all_number_of_ridges.extend(deepcopy(dict_ridge_statistics_year[loc_year]['number_ridges']))
    all_LIDM, all_MKD, all_Dmax, all_number_of_ridges = fill_allYear_data(dict_ridge_statistics_year_all)

    # initilize the figure
    every_nth = 50
    plt.ion()
    figure_weekly_analysis = plt.figure(layout='constrained', figsize=(12,8)) # 4/5 aspect ratio
    gridspec_weekly_analysis = figure_weekly_analysis.add_gridspec(4,6)
    figure_weekly_analysis.suptitle(f"Season   , location   , week   ", fontsize=16)
    # figure ice data
    ax_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0:2,0:4])
    # figure current week ice data
    ax_current_week_ice_data = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,0:2])
    # figure spectogram
    ax_specto = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2:4,2:4])
    # figure mean ridge keel depth
    ax_mean_ridge_keel_depth = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[0,4:6])
    # figure_distubution
    ax_kernel_estimate = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[1,4:6])
    # figure weekly deepest ridge
    ax_weekly_deepest_ridge = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[2,4:6])
    # figure number of ridges
    ax_number_of_ridges = figure_weekly_analysis.add_subplot(gridspec_weekly_analysis[3,4:6])

    # initialize the plots
    dummy_loc = 'a'
    dummy_year = 2004
    dummy_week = 0
    # figure ice data
    ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness = data_analysis_plot.initialize_plot_data_draft(
        ax_ice_data, dateNum, draft, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_dateNum_ridge'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_draft_ridge'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_dateNum'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_start'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_end'], dummy_week, every_nth,
        'Date', 'Draft [m]', [0, 30])

    # figure current week ice data
    ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.initialize_plot_weekly_data_draft(
        ax_current_week_ice_data, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_dateNum'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_draft'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_dateNum_ridge'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_draft_ridge'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['keel_dateNum'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], dummy_week, 'Date', 'Draft [m]', [0, 30], dateTickDistance=2)
    
    # figure spectogram
    ax_specto, colorMesh_specto, thisWeek_patch_specto, scatter_DM, scatter_AM, CP5 = data_analysis_plot.initialize_plot_spectrum(
        ax_specto, draft, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['mean_dateNum'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_start'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_end'], dummy_week)
    
    # figure mean ridge keel depth vs level ice deepest mode
    ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1 = data_analysis_plot.initialize_plot_weekly_data_scatter(
        ax_mean_ridge_keel_depth, all_LIDM, all_MKD, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['mean_keel_draft'], dummy_week, 'Level ice deepest mode [m]', 'Mean keel draft [m]')

    # figure I don't know yet
    ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.initialize_plot_needName(
        ax_kernel_estimate, dateNum, draft, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_start'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_end'], dummy_week, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_expect_deepest_mode'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['peaks_location'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['peaks_intensity'])

    # figure weekly deepest ridge
    ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3 = data_analysis_plot.initialize_plot_weekly_data_scatter(
        ax_weekly_deepest_ridge, all_LIDM, all_Dmax, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['draft_weekly_deepest_ridge'], dummy_week, 'Level ice deepest mode [m]', 'Max weekly draft [m]')

    # figure number of ridges
    ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4 = data_analysis_plot.initialize_plot_weekly_data_scatter(
        ax_number_of_ridges, all_LIDM, all_number_of_ridges, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], 
        dict_ridge_statistics_year_all[dummy_year][dummy_loc]['number_ridges'], dummy_week, 'Level ice deepest mode [m]', 'Number of ridges')


    # iterate over all years and locations
    season_list = list(dict_mooring_locations.keys())
    season_index = 0
    while True:
        print(f"--- Season {season_list[season_index]} ---")
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
        dict_ridge_statistics_corrected = {}
        while True:
            print(f"--- Location {loc_list[loc_index]} ---")
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
            dateNum, draft, _, _, _ = load_data.load_data_oneYear(year, loc, path_to_json_processed, path_to_json_mooring, load_dict_ridge_statistics=False, robustOption=True)
            dict_ridge_statistics = deepcopy(dict_ridge_statistics_year_all[year])
            # add an entry to dict_ridge_statistics[loc] for the week number
            dict_ridge_statistics[loc]['week_number'] = np.arange(0, len(dict_ridge_statistics[loc]['level_ice_deepest_mode']))
            
            # get the number of ridges
            number_ridges = dict_ridge_statistics[loc]['number_ridges']
            # get the indices of ridges that have less than number_ridges_threshold ridges	
            number_ridges_delete = np.where([ridgeNum < number_ridges_threshold for ridgeNum in dict_ridge_statistics[loc]['number_ridges']])
            # if the number of ridges is less than the threshold, delete the data

            # for key in dict_ridge_statistics[loc].keys():
            #     dict_ridge_statistics[loc][key] = remove_indices(dict_ridge_statistics[loc][key], number_ridges_delete)

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

            # set the title of the figure
            figure_weekly_analysis.suptitle(f"Season {season}, location {loc}, week {dict_ridge_statistics[loc]['week_number'][week]}", fontsize=16)
            
            dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]
            xTickLabels = date_time_stuff.datestr(dateNum_every_day, format='DD.MM.YY')

            # figure ice data
            
            ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness = data_analysis_plot.plot_data_draft(
                ax_ice_data, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness,
                dateNum, draft, dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
                dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['week_start'], 
                dict_ridge_statistics[loc]['week_end'], week, every_nth, xTickLabels, [0, 30])

            # figure current week ice data

            ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.plot_weekly_data_draft(
                ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, dict_ridge_statistics[loc]['keel_dateNum'],
                dict_ridge_statistics[loc]['keel_draft'], dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
                dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dateNum_every_day, week, xTickLabels, 
                [0, 30], dateTickDistance=2)
            
            # figure spectogram
            ax_specto, colorMesh_specto, thisWeek_patch_specto, scatter_DM, scatter_AM, CP5 = data_analysis_plot.plot_spectrum(
                ax_specto, colorMesh_specto, thisWeek_patch_specto, scatter_DM, scatter_AM, CP5,
                X, Y, HHi_plot, draft, dict_ridge_statistics[loc]['mean_dateNum'], dateNum_LI, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week)

            # plot the results of this year and location and the results of all years and locations, to compare it
            # figure mean ridge keel depth
            

            ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1 = data_analysis_plot.plot_weekly_data_scatter(
                ax_mean_ridge_keel_depth,  LI_mode_all, LI_mode_thisYear, CP1, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['mean_keel_draft'], week)

            # figure I don't know yet

            ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.plot_needName(
                ax_kernel_estimate,  DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line, dateNum, draft, dict_ridge_statistics[loc]['week_start'], 
                dict_ridge_statistics[loc]['week_end'], week, dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['peaks_location'], dict_ridge_statistics[loc]['peaks_intensity'])

            # figure weekly deepest ridge

            ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3 = data_analysis_plot.plot_weekly_data_scatter(
                ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3, all_LIDM, all_Dmax, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], week)

            # figure number of ridges

            ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4 = data_analysis_plot.plot_weekly_data_scatter(
                ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4, all_LIDM, all_number_of_ridges, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                dict_ridge_statistics[loc]['number_ridges'], week)
            
           
            ### manual correction
            print("--- weekly manual correction ---")
                

            # start of manual correction for this week
            # controll unit is with num block (5 is ok, 2 is downarrow, 8 is uparrow, 4 is leftarraw, 6 is rightarrow, - is minus)
            # rightarrow: value +1, leftarrow: value -1, uparrow: value +5, downarrow: value -5, -: delete value, enter: correct value
            # print('6: value +1, 4: value -1, 8: value +5, 2: value -5, -: delete value, 5: correct value, 0: apply \nif you use num block: make sure num lock is abled')
            delete_indices = []
            first_enter = True
            while True:
                # choose the data point to be corrected in the spectogram (with the 'arrows' (num block))
                dict_to_change = {'level_ice_deepest_mode': dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                                  'mean_keel_draft': dict_ridge_statistics[loc]['mean_keel_draft'], 
                                  'draft_weekly_deepest_ridge': dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], 
                                  'number_ridges': dict_ridge_statistics[loc]['number_ridges']
                                  }
                
                dict_to_change, week, delete_indices, finished, first_enter = navigate_with_numPad(dict_to_change, week, delete_indices, 1, 5, first_enter)

                # replace the values in the dict_ridge_statistics with the corrected values
                for key in dict_to_change.keys():
                    dict_ridge_statistics[loc][key] = deepcopy(dict_to_change[key])

                
                # delete the values that are marked for deletion in every list for the location
                if len(delete_indices) > 0:
                    for key in dict_ridge_statistics[loc].keys():
                        try:
                            dict_ridge_statistics[loc][key] = remove_indices(dict_ridge_statistics[loc][key], delete_indices)
                        except IndexError as e:
                            if key in ['peaks_location', 'peaks_intensity']:
                                dict_ridge_statistics[loc][key] = remove_indices(dict_ridge_statistics[loc][key], delete_indices[:-1])
                                # the last index can be the last element of the list. Peaks_location and peaks_intensity have one element less than the other lists.
                            else:
                                raise e
                    print(f"deleted values of the week {dict_ridge_statistics[loc]['week_number'][delete_indices]}")
                    delete_indices = [] # reset the delete_indices list

                # update the plots
                figure_weekly_analysis.suptitle(f"Season {season}, location {loc}, week {dict_ridge_statistics[loc]['week_number'][week]}", fontsize=16)
                # update the ice data plot
                ax_ice_data, patch_current_week_ice_data = data_analysis_plot.update_plot_data_draft(
                    ax_ice_data, patch_current_week_ice_data, draft, dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week)
                
                # update the current week ice data plot
                ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek = data_analysis_plot.update_plot_weekly_data_draft(
                    ax_current_week_ice_data, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, dict_ridge_statistics[loc]['keel_dateNum'], 
                    dict_ridge_statistics[loc]['keel_draft'], dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
                    dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dateNum_every_day, week, xTickLabels)
                
                ax_specto, CP5 = data_analysis_plot.update_plot_spectrum(
                    ax_specto, CP5, dict_ridge_statistics[loc]['mean_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], week)
                
                ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line = data_analysis_plot.update_plot_needName(
                    ax_kernel_estimate, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line, dateNum, draft, dict_ridge_statistics[loc]['week_start'], 
                    dict_ridge_statistics[loc]['week_end'], week, dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                    dict_ridge_statistics[loc]['peaks_location'], dict_ridge_statistics[loc]['peaks_intensity'])
                
                # update the rectangle to mark the current data point (week)
                # ax_mean_ridge_keel_depth, CP1 = data_analysis_plot.update_plot_weekly_data_scatter(
                #     ax_mean_ridge_keel_depth, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                #     dict_ridge_statistics[loc]['mean_keel_draft'], week, CP1)
                
                ax_mean_ridge_keel_depth, LI_mode_all, LI_mode_thisYear, CP1 = data_analysis_plot.update_plot_weekly_data_scatter_allPoints(
                    ax_mean_ridge_keel_depth, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                    dict_ridge_statistics[loc]['mean_keel_draft'], week, LI_mode_all, LI_mode_thisYear, CP1)
                
                ax_weekly_deepest_ridge, maxDrift_all, maxDrift_thisYear, CP3 = data_analysis_plot.update_plot_weekly_data_scatter_allPoints(
                    ax_weekly_deepest_ridge, all_LIDM, all_Dmax, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                    dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'], week, maxDrift_all, maxDrift_thisYear, CP3)
                
                ax_number_of_ridges, number_of_ridges_all, number_of_ridges_thisYear, CP4 = data_analysis_plot.update_plot_weekly_data_scatter_allPoints(
                    ax_number_of_ridges, all_LIDM, all_number_of_ridges, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
                    dict_ridge_statistics[loc]['number_ridges'], week, number_of_ridges_all, number_of_ridges_thisYear, CP4)
                
                figure_weekly_analysis.canvas.draw()

                if finished:
                    break # break not only the for loop, but also the while loop
                
            dict_ridge_statistics_corrected[loc] = deepcopy(dict_ridge_statistics[loc])
            # store the updated dict_ridge_statistics as json file
            # create the folder 'ridge_statistics_corrected' if it doesn't exist
            if not os.path.exists(os.path.join(path_to_json_corrected)):
                os.makedirs(os.path.join(path_to_json_corrected))
            dict2json.dict2json(dict_ridge_statistics_corrected[loc], os.path.join(path_to_json_corrected, f'ridge_statistics_{year}{loc}.json'))
            print(f"Data for season {season} and location {loc} has been corrected and stored in the folder 'ridge_statistics_corrected'.")
        print(f"Data for season {season} has been corrected.")

    print('--- End of correction process ---')
    return None
            
def fill_allYear_data(dict_ridge_statistics_year_all):
    all_LIDM = []
    all_MKD = []
    all_Dmax = []
    all_number_of_ridges = []
    for year in dict_ridge_statistics_year_all.keys():
        dict_ridge_statistics_year = dict_ridge_statistics_year_all[year]
        for loc_year in dict_ridge_statistics_year.keys():
            all_LIDM.extend(deepcopy(dict_ridge_statistics_year[loc_year]['level_ice_deepest_mode']))
            all_MKD.extend(deepcopy(dict_ridge_statistics_year[loc_year]['mean_keel_draft']))
            all_Dmax.extend(deepcopy(dict_ridge_statistics_year[loc_year]['draft_weekly_deepest_ridge']))
            all_number_of_ridges.extend(deepcopy(dict_ridge_statistics_year[loc_year]['number_ridges']))
    return all_LIDM, all_MKD, all_Dmax, all_number_of_ridges


def navigate_with_numPad(dict_values_to_change, data_index, delete_indices, smallStep, bigStep, first_enter=True, thisIndex=None):
    """ navigate with the numPad through data points and adapt them
    """

    finished = False
    
    if not first_enter:
        thisIndex = data_index
        # add 5 at the beginning of the user_input, because the user has already entered that he/she wants to correct the value
        user_input = '5'
    else:
        # thisIndex = None
        print(f"6: value +{smallStep}, 4: value -{smallStep}, 8: value +{bigStep}, 2: value -{bigStep}, 5: enter -: delete value, 0: finish")
        user_input = input('press enter after your input ')

    for char in user_input:
        if char == '6':
            # rightarrow: value +1
            data_index += smallStep
        elif char == '4':
            # leftarrow: value -1
            data_index -= smallStep
        elif char == '8':
            # uparrow: value +5
            data_index += bigStep
        elif char == '2':
            # downarrow: value -5
            data_index -= bigStep
        elif char == '-':
            # -: delete value
            if thisIndex is None:
                print('no value to delete')
                continue
            delete_indices.append(thisIndex)
            thisIndex = None
        elif char == '5':
            thisIndex = data_index
            if not first_enter:
                first_enter = True
                print('correct the chosen value')
                for key, value in dict_values_to_change.items():
                    print(f"correct the value for {key} with initial value {np.round(value[thisIndex], 3)}")
                    _, dict_values_to_change[key][thisIndex],_,finished,_ = navigate_with_numPad(dict_values_to_change, dict_values_to_change[key][thisIndex], [], 0.1, 1, thisIndex=thisIndex)           
                    if finished:
                        break
            else:
                print('value chosen')
                first_enter = False

        elif char == '0':
            # exit the loop
            finished = True
            break
        else:
            print(f"invalid input: {char}")
            continue

    return dict_values_to_change, data_index, delete_indices, finished, first_enter

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
