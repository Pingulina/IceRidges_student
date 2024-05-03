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


    # iterate over all years and locations
    for season in dict_mooring_locations.keys():
        dict_ridge_statistics_year_all[season] = {}

        
        for loc in dict_mooring_locations[season].keys():
            if len(season.split('-')) > 1:
                year = season.split('-')[0]
            # get the data for the year and location
            dateNum, draft, dict_ridge_statistics, _, _ = load_data.load_data_oneYear(year, loc, path_to_json_processed, path_to_json_mooring)
            
            # get the number of ridges
            number_ridges = dict_ridge_statistics[loc]['number_ridges']
            # get the indices of ridges that have less than number_ridges_threshold ridges	
            number_ridges_delete = np.where([ridgeNum < number_ridges_threshold for ridgeNum in dict_ridge_statistics[loc]['number_ridges']])
            # if the number of ridges is less than the threshold, delete the data
            for key in dict_ridge_statistics[loc].keys():
                dict_ridge_statistics[loc][key] = remove_indices(dict_ridge_statistics[loc][key], number_ridges_delete)

            dict_ridge_statistics_year_all[season][loc] = deepcopy(dict_ridge_statistics[loc])

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
            dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]

            specto_figure = plt.figure()
            specto_ax = specto_figure.add_subplot(111)
            specto_ax.pcolormesh(X, Y, HHi_plot.transpose(), shading='nearest')
            specto_ax.set_ylim([0, 4])
            specto_ax.set_xlabel('Time')
            specto_ax.set_ylabel('Draft')

            specto_ax.set_xlim([dateNum_LI[0]+3.5, dateNum_LI[-1]-10.5])

            patch_current_week_ice_data = specto_ax.fill_between([dict_ridge_statistics[loc]['week_start'][week], dict_ridge_statistics[loc]['week_end'][week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)
            scatter_DM = specto_ax.scatter(dict_ridge_statistics[loc]['mean_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], c='r', s=10, marker='o') # scatter shape: circles

            scatter_AM = specto_ax.scatter(dict_ridge_statistics[loc]['mean_dateNum'], dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], c='b', s=10, marker='^') # scatter shape: triangles

            CP44 = specto_ax.scatter(0, 0, c='r', s=10, marker='s')


            ### continue with fig(1,1) (line 167 in matlab code)
            # all ice thicknesses from this year and location
            keel_draft_flat = [x for xs in dict_ridge_statistics[loc]['keel_draft_ridge'] for x in xs]
            keel_dateNum_flat = [x for xs in dict_ridge_statistics[loc]['keel_dateNum_ridge'] for x in xs]
            draft_figure = plt.figure()
            draft_ax = draft_figure.add_subplot(111)
            draft_ax.set_ylim([0, 5])
            ULS_draft_signal = draft_ax.plot(dateNum, draft, color='tab:blue', label='Raw ULS draft signal', zorder=1)
            RidgePeaks = draft_ax.scatter(keel_dateNum_flat, keel_draft_flat, color='red', label='Individual ridge peaks', s=0.75, zorder=2)
            keel_dateNum_weekStart = [date[0] for date in dict_ridge_statistics[loc]['keel_dateNum']]
            LI_thickness = draft_ax.step(keel_dateNum_weekStart, dict_ridge_statistics[loc]['level_ice_deepest_mode'], where='post', color='black', label='Level ice draft estimate', zorder=3)


            # current ice thickness (of this week)
            draft_thisWeek_figure = plt.figure()
            draft_thisWeek_ax = draft_thisWeek_figure.add_subplot(111)
            draft_thisWeek_ax.set_ylim(0, 5)
            draft_thisWeek_ax.set_ylabel('Draft [m]')
            draft_thisWeek_ax.set_xticks(dateNum_every_day[week*7:(week+1)*7])
            draft_thisWeek_ax.set_xticklabels(date_time_stuff.datestr(dateNum_every_day[week*7:(week+1)*7], format='DD.MM.YY'))
            
            ULS_draft_signal_thisWeek = draft_thisWeek_ax.plot(dict_ridge_statistics[loc]['keel_dateNum'][week], dict_ridge_statistics[loc]['keel_draft'][week], color='tab:blue', label='Raw ULS draft signal', zorder=0)
            RidgePeaks_thisWeek = draft_thisWeek_ax.scatter(dict_ridge_statistics[loc]['keel_dateNum_ridge'][week], dict_ridge_statistics[loc]['keel_draft_ridge'][week], color='red', label='Individual ridge peaks', zorder=1, s=2)
            LI_thickness_thisWeek = draft_thisWeek_ax.step(keel_dateNum_weekStart[week], dict_ridge_statistics[loc]['level_ice_deepest_mode'][week], where='post', color='green', label='Level ice draft estimate', zorder=2)





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
