import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import json
from copy import deepcopy
import scipy.stats

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime as dt
import os
import sys

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module

### imports using the helper function import_module
constants = import_module('constants', 'helper_functions')
load_data = import_module('load_data', 'data_handling')
date_time_stuff = import_module('date_time_stuff', 'helper_functions')
data_analysis_plot = import_module('data_analysis_plot', 'plot_functions')
user_input_iteration = import_module('user_input_iteration', 'user_interaction')
dict2json = import_module('dict2json', 'data_handling')
j2d = import_module('jsonified2dict', 'data_handling')
data_analysis_plot_plotly = import_module('data_analysis_plot_plotly', 'plot_functions')

def weekly_analysis_load_data_all_years():
    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)

    all_LIDM, all_MKD, all_Dmax, all_number_of_ridges = fill_allYear_data(dict_ridge_statistics_year_all)
    # write the data to dict
    dict_iceData_all = {'all_LIDM': all_LIDM, 'all_MKD': all_MKD, 'all_Dmax': all_Dmax, 'all_number_of_ridges': all_number_of_ridges}
    return dict_iceData_all

def weekly_analysis_load_data(year, loc):
    # load the data
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    path_to_json_corrected = os.path.join(constants.pathName_dataResults, 'ridge_statistics_corrected')
    dateNum, draft, _, _, _ = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, 
                                                                         path_to_json_mooring=path_to_json_mooring, load_dict_ridge_statistics=False,
                                                                         year=year, loc=loc
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
    dict_mooring_locations_ridges = {key: dict_mooring_locations[key] for key in dict_mooring_locations.keys() if key[0:4] in mooring_years}

    dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)

    all_LIDM, all_MKD, all_Dmax, all_number_of_ridges = fill_allYear_data(dict_ridge_statistics_year_all)

    return dateNum, draft, dict_ridge_statistics_year_all, dict_mooring_locations_ridges, all_LIDM, all_MKD, all_Dmax, all_number_of_ridges




def weekly_analysis_plot(year, loc, week, dict_ridge_statistics_allYears, dict_ridge_statistics_jsonified, number_ridges_threshold=15):
    ### get the variables out of the dicts
    all_LIDM = dict_ridge_statistics_allYears['all_LIDM']
    all_MKD = dict_ridge_statistics_allYears['all_MKD']
    all_Dmax = dict_ridge_statistics_allYears['all_Dmax']
    all_number_of_ridges = dict_ridge_statistics_allYears['all_number_of_ridges']

    # print(dict_ridge_statistics_jsonified.keys())
    dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified[str(year)][loc]) # this is to convert the jsonified data to a dict with its original data types
    dateNum_LI = dict_ridge_statistics['dateNum_LI']
    draft_mode = dict_ridge_statistics['draft_mode']
    dateNum_rc = dict_ridge_statistics['dateNum_rc']
    draft_rc = dict_ridge_statistics['draft_rc']
    dateNum_rc_pd = dict_ridge_statistics['mean_dateNum']
    draft_deepest_ridge = dict_ridge_statistics['expect_deepest_ridge']
    deepest_mode_weekly = dict_ridge_statistics['level_ice_deepest_mode']
    deepest_mode_expect_weekly = dict_ridge_statistics['level_ice_expect_deepest_mode']
    week_to_keep = dict_ridge_statistics['week_to_keep']  # must be int
    number_ridges = dict_ridge_statistics['number_ridges']
    mean_keel_draft = dict_ridge_statistics['mean_keel_draft']
    draft_max_weekly = 'draft_weekly_deepest_ridge'
    dateNum_reshape = dict_ridge_statistics['keel_dateNum']
    draft_reshape = dict_ridge_statistics['keel_draft']
    draft_ridge = dict_ridge_statistics['keel_draft_ridge']
    dateNum_ridge = dict_ridge_statistics['keel_dateNum_ridge']

    week_starts = dict_ridge_statistics['week_start']
    week_ends = dict_ridge_statistics['week_end']

    dateNum = dict_ridge_statistics['dateNum']
    draft = dict_ridge_statistics['draft']
    keel_draft_flat = [x for xs in draft_ridge for x in xs]
    keel_dateNum_flat = [x for xs in dateNum_ridge for x in xs]
    
    ### preparing stuff
    every_nth = 50
    dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]
    xTickLabels = date_time_stuff.datestr(dateNum_every_day, format='DD.MM.YY')


    # make weekly histogram data that are later used for creating the distogram plot
    period = (24//constants.level_ice_time)*constants.level_ice_statistic_days # hours per sampling unit (week)
    histBins = np.arange(-0.1, 8+0.1, 0.1)

    # instantaneaous LI draft estimated by finding the mode of the distribution. 
    # Multiplication with 1000, finding the mode and subsequent division by 1000 s done because the mode function bins the data in integers. 
    # dateNum_LI is the time of the instantaneous estimates

    d_t = np.round(np.mean(np.diff(dateNum))*3600*24)
    mean_time = 3600 * constants.level_ice_time
    mean_points = mean_time / d_t
    numberElements = int(np.floor(len(dateNum)/mean_points) * mean_points)
    # dateNum_reshape = dateNum[:numberElements]
    # dateNum_reshape = dateNum_reshape.reshape(int(len(dateNum)/mean_points), int(mean_points))
    # draft_reshape = draft[:numberElements]
    # draft_reshape = draft_reshape.reshape(int(len(draft)/mean_points), int(mean_points))

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
    [X_spectogram, Y_spectogram] = np.meshgrid(dateNum_hist, hh)
    # plot the data
    # the figure should contain a spectogram and some lines on top of it (all in one plot)
    HHi_plot = HHi / (period+1)
    



    ### Create a subplot figure
    fig = make_subplots(
        rows=4, cols=6,
        specs=[
            [{"colspan": 4}, None, None, None, {"colspan": 2}, None],
            [{"colspan": 4}, None, None, None, {"colspan": 2}, None],
            [{"colspan": 2}, None, {"colspan": 2}, None, {"colspan": 2}, None],
            [{"colspan": 2}, None, {"colspan": 2}, None, {"colspan": 2}, None]
        ],
        # subplot_titles=(
        #     "Ice Data", "", "", "", "Mean Ridge Keel Depth",
        #     "", "", "", "", "Kernel Estimate",
        #     "Current Week Ice Data", "", "Spectogram", "", "Weekly Deepest Ridge",
        #     "", "", "", "", "Number of Ridges"
        # )
    )

    fig.update_layout(
        title_text=f"Year {year}, location {loc}, week {week}",
        height=800,
        width=1200
    )

    # Example of adding traces to the subplots
    # You need to replace the following with actual data and traces

    #### Plot data draft
    # Add the fill_between equivalent
    fig = data_analysis_plot_plotly.initialize_plot_data_draft(
        fig, row=1, col=1, time=dateNum, draft=draft, time_ridge=dateNum_ridge, draft_ridge=draft_ridge, 
        time_LI=dateNum_reshape, draft_LI=deepest_mode_weekly, week_starts=week_starts, week_ends=week_ends, week=week, 
        every_nth_xTick=50, xlabel='Date all', ylabel='Draft [m]', ylim=[0, 30], xTickLabels=xTickLabels, legend=True
    )

    # Current Week Ice Data
    # fig.add_trace(
    #     go.Scatter(x=dateNum_reshape, y=draft_reshape, mode='lines', name='Keel Draft'),
    #     row=3, col=1
    # )
    fig = data_analysis_plot_plotly.initialize_plot_weekly_data_draft(
        fig, row=3, col=1, time=dateNum_reshape, draft=draft_reshape, time_ridge=dateNum_ridge, draft_ridge=draft_ridge, 
        time_LI=dateNum_reshape, draft_LI=deepest_mode_weekly, week=week, xlabel='Date weekly', ylabel='Draft [m]', ylim=[0, 30], 
        xTickLabels=xTickLabels, dateTickDistance=2)

    # Spectogram
    fig = data_analysis_plot_plotly.initialize_plot_spectrum(
        fig, row=3, col=3, 
        HHi_plot=HHi_plot, X_spectogram=X_spectogram, Y_spectogram=Y_spectogram,
        # HHi_plot=np.zeros((len(dateNum_rc_pd), len(deepest_mode_weekly)), dtype=float), X_spectogram=np.arange(len(dateNum_rc_pd)), Y_spectogram=np.arange(len(deepest_mode_weekly)),
        draft=draft, time_mean=dateNum_rc_pd, LI_deepestMode=deepest_mode_weekly, 
        LI_deepestMode_expect=deepest_mode_expect_weekly, week_starts=week_starts, week_ends=week_ends, 
        week=week, xlabel='Date specto', ylabel='Draft [m]')

    # Mean Ridge Keel Depth
    fig.add_trace(
        go.Scatter(x=all_LIDM, y=all_MKD, mode='markers', name='Mean Keel Draft'),
        row=1, col=5
    )

    # Kernel Estimate
    fig.add_trace(
        go.Scatter(x=dateNum, y=draft, mode='lines', name='Kernel Estimate'),
        row=2, col=5
    )

    # Weekly Deepest Ridge
    fig.add_trace(
        go.Scatter(x=all_LIDM, y=all_Dmax, mode='markers', name='Max Weekly Draft'),
        row=3, col=5
    )

    # Number of Ridges
    fig.add_trace(
        go.Scatter(x=all_LIDM, y=all_number_of_ridges, mode='markers', name='Number of Ridges'),
        row=4, col=5
    )

    # Update layout for better spacing
    fig.update_layout(showlegend=False, title_text="Season , location , week")

    return fig

def weekly_analysis_plot_plotly(year, loc, number_ridges_threshold=15):
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    # load the data
    dateNum, draft, dict_ridge_statistics_year_all, dict_mooring_locations, all_LIDM, all_MKD, all_Dmax, all_number_of_ridges = weekly_analysis_load_data(year, loc)

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
    dummy_loc = loc #'b'
    dummy_year = year # 2005
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

            d_t = np.round(np.mean(np.diff(dateNum))*3600*24)
            mean_time = 3600 * constants.level_ice_time
            mean_points = mean_time / d_t
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