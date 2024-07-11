# content from S007

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime as dt
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
mooring_locs = import_module('mooring_locations', 'helper_functions')
j2np = import_module('json2numpy', 'data_handling')
load_data = import_module('load_data', 'data_handling')
rce = import_module('ridge_compute_extract', 'data_handling')
user_input_iteration = import_module('user_input_iteration', 'user_interaction')



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
    

    dateNum_reshape_hourly, draft_reshape_hourly = rce.extract_hourly_data_draft(dateNum, draft)

    draft_reshape_rounded = np.round(draft_reshape_hourly*1000)
    level_ice_deepest_mode_hourly = [max(set(hourly_data), key=hourly_data.tolist().count) / 1000 for hourly_data in draft_reshape_rounded]

    level_ice_deepest_mode = dict_ridge_statistics[loc]['level_ice_deepest_mode']
    mean_dateNum = dict_ridge_statistics[loc]['mean_dateNum']
    mean_keel_draft = dict_ridge_statistics[loc]['mean_keel_draft']
    level_ice_deepest_mode = dict_ridge_statistics[loc]['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics[loc]['level_ice_expect_deepest_mode']
    newDayIndex = np.where(dateNum.astype(int)-np.roll(dateNum.astype(int), 1)!=0)[0]
    newMonthIndex = np.where([dt.fromordinal(int(dateNum[newDayIndex[i]])).month - dt.fromordinal(int(dateNum[newDayIndex[i-1]])).month for i in range(len(newDayIndex))])
    newMonthIndex = newDayIndex[newMonthIndex]
    dateTicks = [str(dt.fromordinal(thisDate))[0:7] for thisDate in dateNum[newMonthIndex[::2]].astype(int)]
    dateTicks_days = [str(dt.fromordinal(thisDate))[0:10] for thisDate in dateNum[newDayIndex].astype(int)]

    ##### initializing the plot #####
    plt.ion()
    figure_LI_statistics = plt.figure(layout='constrained', figsize=(8,8)) # 4/5 aspect ratio
    gridspec_LI_statistics = figure_LI_statistics.add_gridspec(6,3)
    figure_LI_statistics.suptitle(f"Level ice statistics", fontsize=16)



    ### computations ###
    ############ estimating the level ice statistics for each level_ice_statistics_day period ############

    # ice draft overview
    ax_iceDraft_overview = figure_LI_statistics.add_subplot(gridspec_LI_statistics[2, 0:2])
    ax_iceDraft_overview.plot(dateNum[0:-1:20], draft[0:-1:20], 'tab:blue', label='Ice draft')
    ax_iceDraft_overview.plot(dateNum_LI, draft_LI, 'tab:orange', label='Level ice draft')
    ax_iceDraft_overview.plot(dateNum_LI, level_ice_deepest_mode_hourly, 'tab:red', label='Level ice deepest mode')
    ax_iceDraft_overview.set_title('Ice draft overview')
    ax_iceDraft_overview.set_xlabel('Date')
    ax_iceDraft_overview.set_ylabel('Ice draft [m]')
    ax_iceDraft_overview.legend(loc='upper left')
    ax_iceDraft_overview.set_xticks(dateNum[newMonthIndex[::2]])
    ax_iceDraft_overview.set_xticklabels(dateTicks, rotation=45)


    # histogram parameters
    histBins = int((max(level_ice_deepest_mode_hourly) - min(level_ice_deepest_mode_hourly))/0.1)
    histBins_array = np.arange(min(level_ice_deepest_mode_hourly)-0.1, max(level_ice_deepest_mode_hourly), 0.1)
    period = int((24 / constants.level_ice_time) * constants.level_ice_statistic_days) # number of hours in a level ice statistic period (week)
    ### make weekly histogram data
    # alocate memory for histogram data variables
    hist_levelIce_mode_weekly = np.zeros((int(len(level_ice_deepest_mode_hourly)/period), len(histBins_array)-1))
    dateNum_hist_levelIce_weekly = np.zeros(int(len(level_ice_deepest_mode_hourly)/period))
    hist_levelIce_mode_weekly_dens = np.zeros((int(len(level_ice_deepest_mode_hourly)/period), len(histBins_array)-1))

    for i in range(int(len(level_ice_deepest_mode_hourly)/period)):
        hist_levelIce_mode_weekly[i], _ = np.histogram(level_ice_deepest_mode_hourly[i*period:(i+1)*period], bins=histBins_array)
        hist_levelIce_mode_weekly_dens[i], _ = np.histogram(level_ice_deepest_mode_hourly[i*period:(i+1)*period], bins=histBins_array, density=True)
        dateNum_hist_levelIce_weekly[i] = np.mean(dateNum_LI[i*period:(i+1)*period])

    hist_draft_mode_weekly = np.zeros((int(len(draft_reshape_hourly)/constants.level_ice_statistic_days), len(histBins_array)-1))
    dateNum_hist_draft_weekly = np.zeros(int(len(draft_reshape_hourly)/constants.level_ice_statistic_days))
    hist_draft_mode_weekly_dens = np.zeros((int(len(draft_reshape_hourly)/constants.level_ice_statistic_days), len(histBins_array)-1))
    hist_draft_mode_weekly_points = np.zeros((int(len(draft_reshape_hourly)/constants.level_ice_statistic_days), len(histBins_array)))
    hist_draft_mode_weekly_dens_points = np.zeros((int(len(draft_reshape_hourly)/constants.level_ice_statistic_days), len(histBins_array)))

    for i in range(int(len(draft_reshape_hourly)/constants.level_ice_statistic_days)):
        hist_draft_mode_weekly[i], hist_draft_mode_weekly_points[i] = np.histogram(draft_reshape_hourly[i*constants.level_ice_statistic_days*24:(i+1)*constants.level_ice_statistic_days*24], bins=histBins_array)
        hist_draft_mode_weekly_dens[i], hist_draft_mode_weekly_dens_points[i] = np.histogram(draft_reshape_hourly[i*constants.level_ice_statistic_days*24:(i+1)*constants.level_ice_statistic_days*24], bins=histBins_array, density=True)
        dateNum_hist_draft_weekly[i] = np.mean(dateNum[i*constants.level_ice_statistic_days*24:(i+1)*constants.level_ice_statistic_days*24])

    histBins_mids = histBins_array[0:-1] + np.diff(histBins_array)/2
    [X, Y] = np.meshgrid(dateNum_hist_levelIce_weekly, histBins_mids)
    week = 0



    # initialize the spectrum plot
    # the figure should contain a spectogram and some lines on top of it (all in one plot)
    hist_levelIce_mode_weekly_plot = hist_levelIce_mode_weekly / (period+1)

    ax_iceDraft_spectrum = figure_LI_statistics.add_subplot(gridspec_LI_statistics[0:2, 0:2])
    ax_iceDraft_spectrum, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker = initialize_plot_spectrum(
        ax_iceDraft_spectrum, X, Y, hist_levelIce_mode_weekly.T, {}, dateNum_hist_levelIce_weekly, level_ice_deepest_mode, {}, 
        dateNum_hist_levelIce_weekly, level_ice_expect_deepest_mode, {}, dateNum_hist_levelIce_weekly[0], level_ice_deepest_mode[0], ylim=[0,3], xticks=dateNum[newMonthIndex[::2]])
    

    ax_iceDraft_overview, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker = plot_spectrum(
        ax_iceDraft_spectrum, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker,
        X, Y, hist_levelIce_mode_weekly.T, {}, dateNum_hist_levelIce_weekly, level_ice_deepest_mode, 
        dateNum_hist_levelIce_weekly, level_ice_expect_deepest_mode, dateNum_hist_levelIce_weekly[0], level_ice_deepest_mode[0]
    )

    # level ice mode
    ax_levelIce_mode = figure_LI_statistics.add_subplot(gridspec_LI_statistics[3, 0:2])
    # initialize the line indicating the current mode
    line_levelIce_current_mode = ax_levelIce_mode.plot([0, 0], [0, 12], 'r', zorder=1)
    # initialize the histogram
    ax_levelIce_mode, hist_levelIce_mode = initialize_plot_histogram(ax_levelIce_mode, level_ice_deepest_mode_hourly, {'bins': histBins_array, 'density':True}, xlim=[-0.1, 8], ylim=[0, 4])
    # ax_levelIce_mode, hist_levelIce_mode = plot_histogram(ax_levelIce_mode, hist_levelIce_mode, level_ice_deepest_mode_hourly, {'bins': histBins, 'density':True})
    
    # initialize the plot for weekly histogram
    ax_levelIce_mode_weekly = figure_LI_statistics.add_subplot(gridspec_LI_statistics[0:2, 2])
    ax_levelIce_mode_weekly, line_hist_levelIce_mode_weekly = initialize_plot_histogram(ax_levelIce_mode_weekly, hist_draft_mode_weekly_dens[week], 
                                                                                        {'bins': histBins_array, 'density':True}, hist_points=histBins_array, xlim=[-0.1, 3.1], ylim=[0, 4.1])
    interpolated_histBins_array = np.linspace(histBins_array[0], histBins_array[-1], len(histBins_array)*4)
    ax_levelIce_mode_weekly, line_dist_levelIce_mode_weekly = initialize_plot_distribution(ax_levelIce_mode_weekly, np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), interpolated_histBins_array, {'color':'r'})
    

    ax_levelIce_weekly = figure_LI_statistics.add_subplot(gridspec_LI_statistics[2, 2])
    ax_levelIce_weekly, line_draftLI_weekly = initialize_plot_draft(
        ax_levelIce_weekly, np.concatenate(dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
        np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), {'color':'tab:blue', 'linewidth':0.5}, ylim=[-0.1, 5.1],
        x_ticks=dateNum[newDayIndex[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days:2]], 
        x_ticklabels=dateTicks_days[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days:2])
    ax_levelIce_weekly, line_LI_DM_weekly = initialize_plot_straightLine(
        ax_levelIce_weekly, [dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24], dateNum_reshape_hourly[(week+1)*constants.level_ice_statistic_days*24]], 
        level_ice_deepest_mode[week], {'color':'r', 'linestyle':'--'})


    while True:
        # loop through the weeks
        print("Press 'f' for next week, 'd' for this week and 's' for last week and 'x' to exit the program. You can also enter the week directly. In all cases, press enter afterwards.")
        success, week = user_input_iteration.get_user_input_iteration(week, len(level_ice_deepest_mode))
        if success == -1:
            break
        elif success == 0:
            continue
        elif success == 1:
            pass
        else:
            raise ValueError("Invalid success value.")
        line_levelIce_current_mode[0].set_xdata(np.ones(2)*level_ice_deepest_mode[week])
        ax_levelIce_mode_weekly, line_hist_levelIce_mode_weekly = plot_histogram(ax_levelIce_mode_weekly, line_hist_levelIce_mode_weekly, hist_draft_mode_weekly_dens[week])
        ax_levelIce_mode_weekly, line_dist_levelIce_mode_weekly = update_plot_distribution(ax_levelIce_mode_weekly, line_dist_levelIce_mode_weekly, np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), interpolated_histBins_array)
        currentPoint_marker = update_plot_spectrum(ax_iceDraft_spectrum, currentPoint_marker, dateNum_hist_levelIce_weekly[week], level_ice_deepest_mode[week])
        ax_levelIce_weekly, line_draftLI_weekly = plot_draft(
            ax_levelIce_weekly, line_draftLI_weekly, np.concatenate(dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
            np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
            x_ticks=dateNum[newDayIndex[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days:2]], 
            x_ticklabels=dateTicks_days[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days:2])
        ax_levelIce_weekly, line_LI_DM_weekly = plot_straightLine(
            ax_levelIce_weekly, line_LI_DM_weekly, [dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24][0], dateNum_reshape_hourly[(week+1)*constants.level_ice_statistic_days*24][0]], 
            level_ice_deepest_mode[week])
    print('done')


def initialize_plot_straightLine(ax, x, y, line_properties={}):
    """Plot a straight line on the axis ax with constant y value
    """
    straightLine = ax.plot(x, np.ones(len(x))*y, c=line_properties.get('color', 'r'), linewidth=line_properties.get('linewidth', 1), zorder=0)
    return ax, straightLine[0]

def plot_straightLine(ax, straightLine, x, y):
    """Plot a straight line on the axis ax with constant y value
    """
    straightLine.set_xdata(x)
    straightLine.set_ydata(np.ones(len(x))*y)
    return ax, straightLine

def initialize_plot_draft(ax, dateNum_data, draft_data, draft_properties={}, xlim=None, ylim=None, x_ticks=None, x_ticklabels=None):
    """Plot the draft data on the axis ax with the properties specified in draft_properties
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    draft_line = ax.plot(dateNum_data, draft_data, c=draft_properties.get('color', 'tab:blue'), linewidth=draft_properties.get('linewidth', 1), zorder=0)
    if x_ticks is not None:
        ax.set_xticks(x_ticks)
        if x_ticklabels is not None:
            ax.set_xticklabels(x_ticklabels, rotation=45)
    ax.set_xlim([min(dateNum_data), max(dateNum_data)])
    return ax, draft_line[0]

def plot_draft(ax, draft_line, dateNum_data, draft_data, x_ticks=None, x_ticklabels=None):
    """Plot the draft data on the axis ax with the properties specified in draft_properties
    """
    draft_line.set_xdata(dateNum_data)
    draft_line.set_ydata(draft_data)
    if x_ticks is not None:
        ax.set_xticks(x_ticks)
        if x_ticklabels is not None:
            ax.set_xticklabels(x_ticklabels, rotation=45)
    ax.set_xlim([min(dateNum_data), max(dateNum_data)])
    return ax, draft_line

def initialize_plot_histogram(ax, hist_data, hist_properties, hist_points=None, xlim=None, ylim=None):
    """Plot a histogram of the data in hist_data on the axis ax with the properties specified in hist_properties
    """
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    if hist_points is not None:
        hist_heights = hist_data
    else:
        hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=hist_properties.get('density', False))
        hist_heights = hist_numpy[0]
        hist_points = hist_numpy[1]
    hist_line = ax.bar(hist_points[:-1], hist_heights, align='edge', color=hist_properties.get('color', 'tab:blue'), alpha=hist_properties.get('alpha', 0.5), 
                       zorder=0, width=0.1)
    return ax, hist_line

def plot_histogram(ax, hist_line, hist_data, hist_properties={}):
    """Plot a histogram of the data in hist_data on the axis ax with the properties specified in hist_properties
    """
    if not hist_properties == {}:
        hist_data, _ = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=hist_properties.get('density', False))
    for i in range(len(hist_line)):
        hist_line[i].set_height(hist_data[i])
    # hist_line.remove()
    # hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=hist_properties.get('density', False))
    # hist_line = ax.bar(hist_numpy[1][:-1], hist_numpy[0], align='edge', color=hist_properties.get('color', 'tab:blue'), alpha=hist_properties.get('alpha', 0.5), 
    #                     zorder=0, width=(max(hist_data)-min(hist_data))/hist_properties.get('bins', 10))
    return ax, hist_line

def initialize_plot_distribution(ax, hist_data, line_x, dist_properties={}):
    """Plot a distribution of the data in dist_data on the axis ax fitting for the line_x values on already initialited axis ax
    """
    # prob_distri = scipy.stats.norm.fit(hist_data)
    # line_y = scipy.stats.norm.pdf(line_x, prob_distri[0], prob_distri[1])
    kde = scipy.stats.gaussian_kde(hist_data, bw_method=0.1)
    line_y = kde(line_x)
    dist_line = ax.plot(line_x, line_y, c=dist_properties.get('color','r'), zorder=1)
    return ax, dist_line[0]

def update_plot_distribution(ax, dist_line, hist_data, line_x):
    """Update the line of the distirbtion of the data in hist_data on the axis ax
    """
    # prob_distri = scipy.stats.norm.fit(hist_data)
    # line_y = scipy.stats.norm.pdf(line_x, prob_distri[0], prob_distri[1])
    kde = scipy.stats.kde.gaussian_kde(hist_data, bw_method=0.1)
    line_y = kde(line_x)
    dist_line.set_ydata(line_y)
    return ax, dist_line

def plot_spectrum(ax, colorMesh, scatter1_line, scatter2_line, CP, spec_x, spec_y, spec_z, spec_properties, scatter1_x, scatter1_y, scatter2_x, scatter2_y, currentPoint_x, currentPoint_y):
    """plot a spectrum of the data in x and y on the axis ax with the properties specified in spectrum_properties
    """
    colorMesh.remove()
    colorMesh = ax.pcolormesh(spec_x, spec_y, spec_z, shading=spec_properties.get('shading', 'nearest'))
    scatter1_line.set_offsets(np.c_[scatter1_x, scatter1_y])
    scatter2_line.set_offsets(np.c_[scatter2_x, scatter2_y])
    lrs1x = (ax.get_xlim()[1]-ax.get_xlim()[0])/20
    lrs1y = (ax.get_ylim()[1]-ax.get_ylim()[0])/20
    CP.set_xy([currentPoint_x-lrs1x/2, currentPoint_y-lrs1y/2])
    # add the patch to the axis
    ax.add_patch(CP)

    return ax, colorMesh, scatter1_line, scatter2_line, CP


def initialize_plot_spectrum(ax, spec_x, spec_y, spec_z, spec_properties, scatter1_x, scatter1_y, scatter1_properties, scatter2_x, scatter2_y, scatter2_properties, currentPoint_x, currentPoint_y, xlim=None, ylim=None, xticks=None):
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    if xticks is not None:
        ax.set_xticks(xticks)
    colorMesh = ax.pcolormesh(spec_x, spec_y, spec_z, shading=spec_properties.get('shading', 'nearest'))

    scatter1_line = ax.scatter(scatter1_x, scatter1_y, c=scatter1_properties.get('color','r'), s=scatter1_properties.get('size', 10), marker=scatter1_properties.get('marker','o'), zorder=2) # scatter shape: circles
    scatter2_line = ax.scatter(scatter2_x, scatter2_y, c=scatter2_properties.get('color','b'), s=scatter2_properties.get('size', 10), marker=scatter2_properties.get('marker','^'), zorder=3) # scatter shape: triangles
    lrs1x = (ax.get_xlim()[1]-ax.get_xlim()[0])/20
    lrs1y = (ax.get_ylim()[1]-ax.get_ylim()[0])/20
    CP = mpatches.Rectangle((currentPoint_x-lrs1x/2, currentPoint_y-lrs1y/2), lrs1x, lrs1y, edgecolor='r', facecolor='none', zorder=4) # time_mean[week]
    # CP = mpatches.Rectangle((spec_x[week]-lrs1x/2, spec_y[week]-lrs1y/2), lrs1x, lrs1y, edgecolor='r', facecolor='none', zorder=4)
    # add the patch to the axis
    ax.add_patch(CP)

    return ax, colorMesh, scatter1_line, scatter2_line, CP


def update_plot_spectrum(ax, CP, currentPoint_x, currentPoint_y):
    """update the current point marker in spectrum plot
    :param CP: current point line
    :param currentPoint_x: x-coordinate of current point
    :param currentPoint_y: y-coordinate of current point
    :return: CP
    """
    lrs1x = (ax.get_xlim()[1]-ax.get_xlim()[0])/20
    lrs1y = (ax.get_ylim()[1]-ax.get_ylim()[0])/20
    CP.set_xy([currentPoint_x-lrs1x/2, currentPoint_y-lrs1y/2])
    return CP