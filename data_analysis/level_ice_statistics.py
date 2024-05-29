# content from S007

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from datetime import datetime as dt

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
mooring_locs = import_module('mooring_locations', 'helper_functions')
j2np = import_module('json2numpy', 'data_handling')
load_data = import_module('load_data', 'data_handling')
rce = import_module('ridge_compute_extract', 'data_handling')


def level_ice_statistics(year=None, loc=None):
    """Analysing the level ice data, determine the level ice mode for each week
    """
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
            if loc in dict_mooring_locations[year]:
                break
            else:
                print(f"The location {loc} is not in the mooring data. Possible locations are: {dict_mooring_locations[year]}")

    season = list_seasons[list_years.index(year)]

    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')

    sucess2, dateNum_rc, draft_rc, _ = j2np.json2numpy(os.path.join(path_to_json_mooring, f"mooring_{season}_ridge.json"), loc)
    sucess3, dateNum_LI, draft_LI, draft_mode = j2np.json2numpy(os.path.join(path_to_json_mooring, f"mooring_{season}_LI.json"), loc)
    if not (sucess2 and sucess3):
        print(f"Data for {loc} in {year} not found.")
        return None
    

    # load the results from ridge_statistics to avoid recomputing values
    pathName_ridgeStatistics = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    dateNum, draft, dict_ridge_statistics, year, loc = load_data.load_data_oneYear(path_to_json_processed=pathName_ridgeStatistics, path_to_json_mooring=path_to_json_mooring,
                                                                                             year=year, loc=loc, skip_nonexistent_locs=True)


    dateNum_reshape, draft_reshape = rce.extract_weekly_data_draft(dateNum, draft)

    level_ice_deepest_mode = dict_ridge_statistics[loc]['level_ice_deepest_mode']
    mean_dateNum = dict_ridge_statistics[loc]['mean_dateNum']
    mean_keel_draft = dict_ridge_statistics[loc]['mean_keel_draft']
    newDayIndex = np.where(dateNum.astype(int)-np.roll(dateNum.astype(int), 1)!=0)[0]
    newMonthIndex = np.where([dt.fromordinal(int(dateNum[newDayIndex[i]])).month - dt.fromordinal(int(dateNum[newDayIndex[i-1]])).month for i in range(len(newDayIndex))])
    newMonthIndex = newDayIndex[newMonthIndex]
    dateTicks = [str(dt.fromordinal(thisDate))[0:7] for thisDate in dateNum[newMonthIndex[::2]].astype(int)]

    ##### initializing the plot #####
    plt.ion()
    figure_LI_statistics = plt.figure(layout='constrained', figsize=(8,8)) # 4/5 aspect ratio
    gridspec_LI_statistics = figure_LI_statistics.add_gridspec(6,3)
    figure_LI_statistics.suptitle(f"Level ice statistics", fontsize=16)



    ### computations ###
    ############ estimating the level ice statistics for each level_ice_statistics_day period ############

    # ice draft overview
    ax_iceDraft_overview = figure_LI_statistics.add_subplot(gridspec_LI_statistics[0, 0:2])
    ax_iceDraft_overview.plot(dateNum[0:-1:20], draft[0:-1:20], 'tab:blue', label='Ice draft')
    ax_iceDraft_overview.plot(dateNum_LI, draft_LI, 'tab:orange', label='Level ice draft')
    ax_iceDraft_overview.set_title('Ice draft overview')
    ax_iceDraft_overview.set_xlabel('Date')
    ax_iceDraft_overview.set_ylabel('Ice draft [m]')
    ax_iceDraft_overview.legend(loc='upper right')
    ax_iceDraft_overview.set_xticks(dateNum[newMonthIndex[::2]])
    ax_iceDraft_overview.set_xticklabels(dateTicks, rotation=45)

    # level ice mode
    ax_levelIce_mode = figure_LI_statistics.add_subplot(gridspec_LI_statistics[1, 0:2])
    # initialize the line indicating the current mode
    line_levelIce_current_mode = ax_levelIce_mode.plot([0, 0], [0, 12], 'r', zorder=1)
    # initialize the histogram
    ax_levelIce_mode, hist_levelIce_mode = plot_histogram(ax_levelIce_mode, level_ice_deepest_mode, {'bins': 80}, xlim=[-0.1, 8])
    print('done')



def plot_histogram(ax, hist_data, hist_properties, xlim=None, ylim=None):
    """Plot a histogram of the data in hist_data on the axis ax with the properties specified in hist_properties
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10))
    hist_line = ax.bar(hist_numpy[1][:-1], hist_numpy[0], align='edge', color=hist_properties.get('color', 'tab:blue'), alpha=hist_properties.get('alpha', 0.5), 
                       zorder=0, width=(max(hist_data)-min(hist_data))/hist_properties.get('bins', 10))
    return ax, hist_line