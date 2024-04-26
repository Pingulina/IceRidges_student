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

def weekly_visual_analysis(number_ridges_threshold=15):
    """correct the data manually
    :input: number_ridges_threshold: int: minimal number of ridges per dataset
    """

    # load the data
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    path_to_json_processed = os.path.join(constants.pathName_data, 'ridge_statistics')
    dateNum, draft, dict_ridge_statistics = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, path_to_json_mooring=path_to_json_mooring
                                                                        )
    
    
    # get the data for all years and locations each in an array
    # in Data_results/ridge_statistics/ridge_statistics_{year}.json the data is stored in the following format:
    # dict_ridge_statistics = {loc1: {'data_name' : data, 'data_name' : data, ... }, loc2: {'data_name' : data, 'data_name' : data, ...}, ...}

    # list all files in the directory
    files = os.listdir(path_to_json_processed)
    # sort the files by year
    files.sort()

    dict_ridge_statistics_year_all = {}

    # dict_ridge_statistics_year_all = load_data.load_data_all_years(path_to_json_processed=path_to_json_processed)

    # # for every year and location, get the number of ridges. If there are less than number_ridges_threshold ridges, delete the data
    # for year in dict_ridge_statistics_year_all.keys():
    #     for loc in dict_ridge_statistics_year_all[year].keys():
    #         if len(dict_ridge_statistics_year_all[year][loc]['number_ridges']) < number_ridges_threshold:
    #             del dict_ridge_statistics_year_all[year][loc]


    # iterate over all years and locations
    for year in dict_ridge_statistics_year_all.keys():
        for loc in dict_ridge_statistics_year_all[year].keys():
            # get the data for the year and location
            dateNum, draft, dict_ridge_statistics, _, _ = load_data.load_data_oneYear(year, loc, path_to_json_mooring, path_to_json_processed)
            # get the number of ridges
            number_ridges = dict_ridge_statistics['number_ridges']
            # get the number of ridges that are not nan
            number_ridges_not_nan = np.sum(~np.isnan(number_ridges))
            # if the number of ridges is less than the threshold, delete the data
            if number_ridges_not_nan < number_ridges_threshold:
                del dict_ridge_statistics_year_all[year][loc]

            # make weekly histogram data that are later used for creating the distogram plot
            period = (24/constants.level_ice_time)*constants.level_ice_statistic_days
            histBins = np.arange(-0.1, 8, 0.1)

            # instantaneaous LI draft estimated by finding the mode of the distribution. 
            # Multiplication with 1000, finding the mode and subsequent division by 1000 s done because the mode function bins the data in integers. 
            # dateNum_LI is the time of the instantaneous estimates

            hi = max(dict_ridge_statistics['keel_draft'], key=dict_ridge_statistics['keel_draft'].count)
            dateNum_LI = dict_ridge_statistics['keel_dateNum'][dict_ridge_statistics['keel_draft'].index(hi)]

            numberElements = len(hi)//period
            HHi = [[]]*numberElements
            dateNum_hist = [[]]*numberElements

            for i in range(numberElements):
                # interpolate hi[i*period:(i+1)*period] to get the values for the points histBins
                HHi[i] = np.digitize(hi[i*period:(i+1)*period], histBins) # equivalent to histcounts in matlab, returns the indices of the bins to which each value in input array belongs.
                dateNum_hist[i] = np.mean(dateNum_LI[i*period:(i+1)*period])

            hh = histBins[0:-1]+np.diff(histBins)/2
            [X, Y] = np.meshgrid(dateNum_hist, hh)
            # plot the data
            # the figure should contain a spectogram and some lines on top of it (all in one plot)
            HHi_plot = HHi / (period+1)
            # plot the data
            specto_figure = plt.figure()
            specto_ax = specto_figure.add_subplot(111)
            specto_ax.pcolormesh(X, Y, HHi_plot, shading='auto')
            
            specto_ax.set_xlabel('Time')
            specto_ax.set_ylabel('Draft')

            specto_ax.set_xlim([dateNum_LI[0]+3.5, dateNum_LI[-1]-10.5])

            scatter_DM = specto_ax.scatter(dateNum_LI, dict_ridge_statistics['level_ice_deepest_mode'], 10*np.ones(len(dateNum_LI)), c='r', s=10, marker='o') # scatter shape: circles
            scatter_AM = specto_ax.scatter(dateNum_LI, dict_ridge_statistics['level_ice_expect_deepest_mode'], 10*np.ones(len(dateNum_LI)), c='b', s=10, marker='^') # scatter shape: triangles

            CP44 = specto_ax.scatter(0, 0, 10, c='r', s=10, marker='s')


            ### continue with fig(1,1) (line 167 in matlab code)

            

