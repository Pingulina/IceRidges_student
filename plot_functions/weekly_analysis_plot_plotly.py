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
data_analysis_plot_plotly_initialize = import_module('data_analysis_plot_plotly_initialize', 'plot_functions')

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
    draft_max_weekly = dict_ridge_statistics['draft_weekly_deepest_ridge']
    dateNum_reshape = dict_ridge_statistics['keel_dateNum']
    draft_reshape = dict_ridge_statistics['keel_draft']
    draft_ridge = dict_ridge_statistics['keel_draft_ridge']
    dateNum_ridge = dict_ridge_statistics['keel_dateNum_ridge']

    week_starts = dict_ridge_statistics['week_start']
    week_ends = dict_ridge_statistics['week_end']

    peaks_location = dict_ridge_statistics['peaks_location']
    peaks_intensity = dict_ridge_statistics['peaks_intensity']

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
    dateNum_reshape_hourly = dateNum[:numberElements]
    dateNum_reshape_hourly = dateNum_reshape_hourly.reshape(int(len(dateNum)/mean_points), int(mean_points))
    draft_reshape_hourly = draft[:numberElements]
    draft_reshape_hourly = draft_reshape_hourly.reshape(int(len(draft)/mean_points), int(mean_points))

    hi = compute_mode(np.array(np.round(np.array(draft_reshape_hourly)*1000, 0))) / 1000
    hi_1 = scipy.stats.mode(np.round(np.array(draft_reshape_hourly)*1000, 0), axis=1).mode / 1000
    dateNum_LI = np.mean(dateNum_reshape_hourly, axis=1)

    HHi = [[]] * (len(hi)//period )
    dateNum_hist = [[]] * (len(hi)//period )

    for i, n in enumerate(range(0,len(hi)-period,period)):
        # interpolate hi[i*period:(i+1)*period] to get the values for the points histBins
        HHi[i], _ = np.histogram(hi[n:n+period], bins=histBins) # equivalent to histcounts in matlab, returns the indices of the bins to which each value in input array belongs.
        dateNum_hist[i] = np.mean(dateNum_LI[n:n+period])
    HHi = np.array(HHi)
    hh = histBins[0:-1]+np.diff(histBins)/2
    [X_spectogram, Y_spectogram] = np.meshgrid(dateNum_hist, hh)
    # plot the data
    # the figure should contain a spectogram and some lines on top of it (all in one plot)
    HHi_plot = HHi / (period+1)
    # print('dateNum_hist: ', dateNum_hist)
    # print('hh: ', hh)
    

    ### Create a subplot figure
    fig = make_subplots(
        rows=4, cols=6,
        specs=[
            [{"colspan": 4}, None, None, None, {"colspan": 2}, None],
            [{"colspan": 4}, None, None, None, {"colspan": 2}, None],
            [{"colspan": 4, "rowspan":2}, None, None, None, {"colspan": 2}, None],
            [None, None, None, None, {"colspan": 2}, None]
        ],
        # subplot_titles=(
        #     "Ice Data", "", "", "", "Mean Ridge Keel Depth",
        #     "", "", "", "", "Kernel Estimate",
        #     "Current Week Ice Data", "", "Spectogram", "", "Weekly Deepest Ridge",
        #     "", "", "", "", "Number of Ridges"
        # ),
    	horizontal_spacing=0.1,
    )

    fig.update_layout(
        title_text=f"Year {year}, location {loc}, week {week}",
        height=800,
        width=1200,
        showlegend=False
    )

    #### Plot data draft
    # Draft for whole season for this location
    fig, draftAll_patch_trace_index, draftAll_trace_index, draftAll_peaks_trace_index, draftAll_LIdraft_e_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_data_draft(
        fig, row=1, col=1, time=dateNum, draft=draft, time_ridge=dateNum_ridge, draft_ridge=draft_ridge, 
        time_LI=dateNum_reshape, draft_LI=deepest_mode_weekly, week_starts=week_starts, week_ends=week_ends, week=week, 
        every_nth_xTick=50, xlabel='Date all', ylabel='Draft [m]', ylim=[0, 30], xTickLabels=xTickLabels, legend=True
    )
    # Current week draft
    fig, draftThis_trace_index, draftThis_peaks_trace_index, draftThis_LIdraft_e_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_weekly_data_draft(
        fig, row=2, col=1, time=dateNum_reshape, draft=draft_reshape, time_ridge=dateNum_ridge, draft_ridge=draft_ridge, 
        time_LI=dateNum_reshape, draft_LI=deepest_mode_weekly, week=week, xlabel='Date weekly', ylabel='Draft [m]', ylim=[0, 30], 
        xTickLabels=xTickLabels, dateTickDistance=2)

    # Spectogram
    fig, heatmap_trace_index, heatmap_patch_trace_index, heatmap_LIDM_trace_index, heatmap_LIDMe_trace_index, heatmap_marker_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_spectrum(
        fig, row=3, col=1, 
        HHi_plot=HHi_plot, X_spectogram=X_spectogram, Y_spectogram=Y_spectogram,
        # HHi_plot=np.zeros((len(dateNum_rc_pd), len(deepest_mode_weekly)), dtype=float), X_spectogram=np.arange(len(dateNum_rc_pd)), Y_spectogram=np.arange(len(deepest_mode_weekly)),
        time=dateNum_reshape, draft=draft, time_mean=dateNum_rc_pd, LI_deepestMode=deepest_mode_weekly, 
        LI_deepestMode_expect=deepest_mode_expect_weekly, week_starts=week_starts, week_ends=week_ends, 
        week=week, xlabel='Date specto', ylabel='Draft [m]', xTickLabels=xTickLabels)

    # Mean Ridge Keel Depth
    fig, meanKeelDraft_all_trace_index, meanKeelDraft_this_trace_index, meanKeelDraft_marker_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_weekly_data_scatter(
        fig, row=1, col=5, xData_all=all_LIDM, yData_all=all_MKD, xData_thisYear=deepest_mode_weekly, yData_thisYear=mean_keel_draft, 
        week=week, xlabel='Level ice deepest mode [m]', ylabel='Mean keel draft [m]')

    # Kernel Estimate
    fig, kernelExt_hist_trace_index, kernelEst_LIDM_trace_index, kernelEst_LIDM_trace_index, kernelEst_trace_index, kernelEst_peak_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_kernelEstimation(
        fig, row=2, col=5, time=dateNum, draft=draft, week_starts=week_starts, week_ends=week_ends, week=week, 
        LI_deepestMode_expect=deepest_mode_expect_weekly, LI_deepestMode=deepest_mode_weekly, 
        peaks_location=peaks_location, peaks_intensity=peaks_intensity, xlabel='Draft [m]', ylabel='Kernel estimate [-]')

    # Weekly Deepest Ridge
    fig, maxKeelDraft_all_trace_index, maxKeelDraft_this_trace_index, maxKeelDraft_marker_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_weekly_data_scatter(
        fig, row=3, col=5, xData_all=all_LIDM, yData_all=all_Dmax, xData_thisYear=deepest_mode_weekly, yData_thisYear=draft_max_weekly, 
        week=week, xlabel='Level ice deepest mode [m]', ylabel='Deepest keel draft [m]')

    # Number of Ridges
    fig, numRidges_all_trace_index, numRidges_this_trace_index, numRidges_marker_trace_index = data_analysis_plot_plotly_initialize.initialize_plot_weekly_data_scatter(
        fig, row=4, col=5, xData_all=all_LIDM, yData_all=all_number_of_ridges, xData_thisYear=deepest_mode_weekly, yData_thisYear=number_ridges, 
        week=week, xlabel='Level ice deepest mode [m]', ylabel='Number of ridges [-]')
    

    # write all trace indices in a dict
    dict_trace_indices = {
        'draftAll_patch_trace_index': draftAll_patch_trace_index,
        'draftAll_trace_index': draftAll_trace_index,
        'draftAll_peaks_trace_index': draftAll_peaks_trace_index,
        'draftAll_LIdraft_e_trace_index': draftAll_LIdraft_e_trace_index,
        'draftThis_trace_index': draftThis_trace_index,
        'draftThis_peaks_trace_index': draftThis_peaks_trace_index,
        'draftThis_LIdraft_e_trace_index': draftThis_LIdraft_e_trace_index,
        'heatmap_trace_index': heatmap_trace_index,
        'heatmap_patch_trace_index': heatmap_patch_trace_index,
        'heatmap_LIDM_trace_index': heatmap_LIDM_trace_index,
        'heatmap_LIDMe_trace_index': heatmap_LIDMe_trace_index,
        'heatmap_marker_trace_index': heatmap_marker_trace_index,
        'meanKeelDraft_all_trace_index': meanKeelDraft_all_trace_index,
        'meanKeelDraft_this_trace_index': meanKeelDraft_this_trace_index,
        'meanKeelDraft_marker_trace_index': meanKeelDraft_marker_trace_index,
        'kernelExt_hist_trace_index': kernelExt_hist_trace_index,
        'kernelEst_LIDM_trace_index': kernelEst_LIDM_trace_index,
        'kernelEst_trace_index': kernelEst_trace_index,
        'kernelEst_peak_trace_index': kernelEst_peak_trace_index,
        'maxKeelDraft_all_trace_index': maxKeelDraft_all_trace_index,
        'maxKeelDraft_this_trace_index': maxKeelDraft_this_trace_index,
        'maxKeelDraft_marker_trace_index': maxKeelDraft_marker_trace_index,
        'numRidges_all_trace_index': numRidges_all_trace_index,
        'numRidges_this_trace_index': numRidges_this_trace_index,
        'numRidges_marker_trace_index': numRidges_marker_trace_index
    }

    return fig, dict_trace_indices



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