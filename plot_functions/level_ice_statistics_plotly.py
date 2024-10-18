import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import scipy.stats
import numpy as np
import sys
import os

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
dts = import_module('date_time_stuff', 'helper_functions')
j2d = import_module('jsonified2dict', 'data_handling')



def level_ice_statistics(year, loc, week, dict_ridge_statistics_allYears, dict_ridge_statistics_jsonified):
    """Analysing the level ice data, determine the level ice mode for each week
    """
    ### get the variables out of the dicts
    all_LIDM = dict_ridge_statistics_allYears['all_LIDM']
    all_MKD = dict_ridge_statistics_allYears['all_MKD']
    all_Dmax = dict_ridge_statistics_allYears['all_Dmax']
    all_number_of_ridges = dict_ridge_statistics_allYears['all_number_of_ridges']

    # print(dict_ridge_statistics_jsonified.keys())
    dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified[str(year)][loc]) # this is to convert the jsonified data to a dict with its original data types
    dateNum_LI = dict_ridge_statistics['dateNum_LI']
    draft_LI = dict_ridge_statistics['draft_LI']
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
    

    # extract the hourly data
    dateNum_reshape_hourly, draft_reshape_hourly = rce.extract_hourly_data_draft(dateNum, draft) #, start_at_midnight=True, end_at_midnight=True)

    draft_reshape_rounded = np.round(draft_reshape_hourly*1000)
    level_ice_deepest_mode_hourly = [max(set(hourly_data), key=hourly_data.tolist().count) / 1000 for hourly_data in draft_reshape_rounded]


    ### histogram parameters
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
        hist_draft_mode_weekly[i], hist_draft_mode_weekly_points[i] = np.histogram(draft_reshape_hourly[i*constants.level_ice_statistic_days*24:(i+1)*constants.level_ice_statistic_days*24], 
                                                                                   bins=histBins_array)
        hist_draft_mode_weekly_dens[i], hist_draft_mode_weekly_dens_points[i] = np.histogram(
            draft_reshape_hourly[i*constants.level_ice_statistic_days*24:(i+1)*constants.level_ice_statistic_days*24], bins=histBins_array, density=True
            )
        dateNum_hist_draft_weekly[i] = np.mean(dateNum[i*constants.level_ice_statistic_days*24:(i+1)*constants.level_ice_statistic_days*24])

    histBins_mids = histBins_array[0:-1] + np.diff(histBins_array)/2
    [X, Y] = np.meshgrid(dateNum_hist_levelIce_weekly, histBins_mids)
    
    ### parameters/data
    mean_dateNum = dict_ridge_statistics[loc]['mean_dateNum']
    mean_keel_draft = dict_ridge_statistics[loc]['mean_keel_draft']
    level_ice_deepest_mode = dict_ridge_statistics[loc]['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics[loc]['level_ice_expect_deepest_mode']
    newHourIndex = np.where((dateNum*constants.hours_day).astype(int)-np.roll((dateNum*constants.hours_day).astype(int), 1)!=0)[0]
    newDayIndex = np.where(dateNum.astype(int)-np.roll(dateNum.astype(int), 1)!=0)[0]
    newMonthIndex = np.where([dt.fromordinal(int(dateNum[newDayIndex[i]])).month - dt.fromordinal(int(dateNum[newDayIndex[i-1]])).month for i in range(len(newDayIndex))])
    newMonthIndex = newDayIndex[newMonthIndex]
    dateTicks = [str(dt.fromordinal(thisDate))[0:7] for thisDate in dateNum[newMonthIndex[::2]].astype(int)]
    dateTicks_days = [str(dt.fromordinal(thisDate))[0:10] for thisDate in dateNum[newDayIndex].astype(int)]
    dateTicks_hours = [dts.datestr_hour(thisDate, format='HH:mm:ss') for thisDate in dateNum[newHourIndex]]

    ##### initializing the plot #####
    figure_LI_statistics = make_subplots(
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

    figure_LI_statistics.update_layout(
        title_text=f"Level ice statistics {year} {loc}",
        height=800,
        width=1200,
        showlegend=False
    )



    ### computations ###
    ############ estimating the level ice statistics for each level_ice_statistics_day period ############



    # histogram parameters

    week = 0
    day = 0

    ### ice draft overview spectrum
    # initialize the spectrum plot
    # the figure should contain a spectogram and some lines on top of it (all in one plot)
    hist_levelIce_mode_weekly_plot = hist_levelIce_mode_weekly / (period+1)

    figure_LI_statistics, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker = initialize_plot_spectrum(
        fig=figure_LI_statistics, row=0, col=0, spec_x=X, spec_y=Y, spec_z=hist_levelIce_mode_weekly.T, spec_properties={}, 
        scatter1_x=dateNum_hist_draft_weekly, scatter1_y=level_ice_deepest_mode, scatter1_properties={}, 
        scatter2_x=dateNum_hist_levelIce_weekly, scatter2_y=level_ice_expect_deepest_mode, scatter2_properties={}, 
        currentPoint_x=dateNum_hist_levelIce_weekly[0], currentPoint_y=level_ice_deepest_mode[0], ylim=[0, 3], xticks=dateNum[newMonthIndex[::2]],
        xTitle='Date', yTitle='Level ice draft [m]', title='Level ice draft spectrum')
    

    figure_LI_statistics, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker = plot_spectrum(
        figure_LI_statistics, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker,
        X, Y, hist_levelIce_mode_weekly.T, {}, dateNum_hist_levelIce_weekly, level_ice_deepest_mode, 
        dateNum_hist_levelIce_weekly, level_ice_expect_deepest_mode, dateNum_hist_levelIce_weekly[0], level_ice_deepest_mode[0]
    )
    # ax_iceDraft_spectrum.set_xticks(dateNum[newMonthIndex[::2]])
    # ax_iceDraft_spectrum.set_xticklabels(dateTicks) #, rotation=45)

    # ice draft overview
    ax_iceDraft_overview = figure_LI_statistics.add_subplot(gridspec_LI_statistics[2:4, 0:3])
    line_iceDraft_ice = ax_iceDraft_overview.plot(dateNum[0:-1:20], draft[0:-1:20], 'blue', label='Ice draft', zorder=1)
    line_iceDraft_LI = ax_iceDraft_overview.plot(dateNum_LI, draft_LI, 'orange', label='Level ice draft', zorder=2)
    line_iceDraft_LIDM = ax_iceDraft_overview.plot(dateNum_LI, level_ice_deepest_mode_hourly, 'red', label='Level ice deepest mode', zorder=3)
    line_iceDraft_LIDM_expect = ax_iceDraft_overview.plot(dateNum_hist_levelIce_weekly, level_ice_expect_deepest_mode, 'olive', label='LI expected deepest mode', zorder=4)
    currentWeekPatch = mpatches.Rectangle((dateNum[newDayIndex[week*constants.level_ice_statistic_days]], 0), constants.level_ice_statistic_days, 30, 
                                          edgecolor='None', facecolor='red', alpha=0.3, zorder=4)
    line_iceDraft_currentWeekPatch = ax_iceDraft_overview.add_patch(currentWeekPatch)
    ax_iceDraft_overview.set_title('Ice draft overview')
    ax_iceDraft_overview.set_xlabel('Date')
    ax_iceDraft_overview.set_ylabel('Ice draft [m]')
    # ax_iceDraft_overview.legend(loc='upper left')
    ax_iceDraft_overview.set_xticks(dateNum[newMonthIndex[::2]])
    ax_iceDraft_overview.set_xticklabels(dateTicks) #, rotation=45)
    ax_iceDraft_overview.set_ylim([-0.1, 30])
    ax_iceDraft_overview.invert_yaxis() # make the y-axis upside down, since it is the ice depth plotted

    ### level ice mode of the whole season
    ax_levelIce_mode = figure_LI_statistics.add_subplot(gridspec_LI_statistics[3:6, 3])
    ax_levelIce_mode.set_title('Level ice mode')
    ax_levelIce_mode.set_xlabel('Ice draft [m]')
    ax_levelIce_mode.set_ylabel('Density [-]')
    # initialize the line indicating the current mode
    line_levelIce_current_mode = ax_levelIce_mode.plot([0, 0], [0, 12], 'red', zorder=1)
    # initialize the histogram
    ax_levelIce_mode, hist_levelIce_mode = initialize_plot_histogram(ax_levelIce_mode, level_ice_deepest_mode_hourly, {'bins': histBins_array, 'density':True}, xlim=[-0.1, 8], ylim=[0, 4])
    # ax_levelIce_mode, hist_levelIce_mode = plot_histogram(ax_levelIce_mode, hist_levelIce_mode, level_ice_deepest_mode_hourly, {'bins': histBins, 'density':True})
    
    ### level ice mode weekly
    ax_levelIce_mode_weekly = figure_LI_statistics.add_subplot(gridspec_LI_statistics[0:3, 3])
    ax_levelIce_mode_weekly.set_title('Weekly level ice mode')
    ax_levelIce_mode_weekly.set_xlabel('Ice draft [m]')
    ax_levelIce_mode_weekly.set_ylabel('Density [-]')
    ax_levelIce_mode_weekly, line_hist_levelIce_mode_weekly = initialize_plot_histogram(ax_levelIce_mode_weekly, hist_draft_mode_weekly_dens[week], 
                                                                                        {'bins': histBins_array, 'density':True}, hist_points=histBins_array, xlim=[-0.1, 3.1], ylim=[0, 4.1])
    interpolated_histBins_array = np.linspace(histBins_array[0], histBins_array[-1], len(histBins_array)*4)
    ax_levelIce_mode_weekly, line_dist_levelIce_mode_weekly = initialize_plot_distribution(
        ax_levelIce_mode_weekly, np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
        interpolated_histBins_array, {'color':'red'})
    

    ### plot weekly level ice thickness
    ax_levelIce_weekly = figure_LI_statistics.add_subplot(gridspec_LI_statistics[4:6, 0:3])
    ax_levelIce_weekly.set_title('Weekly level ice draft')
    ax_levelIce_weekly.set_xlabel('Date')
    ax_levelIce_weekly.set_ylabel('Ice draft [m]') 
    ax_levelIce_weekly, line_draftLI_weekly = initialize_plot_draft(
        ax_levelIce_weekly, np.concatenate(dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
        np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
        {'color':'blue', 'linewidth':0.5}, ylim=[-0.1, 5.1],
        x_ticks=dateNum[newDayIndex[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days+1][1::2]], 
        x_ticklabels=dateTicks_days[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days+1][1::2])
    ax_levelIce_weekly, line_LI_DM_weekly = initialize_plot_straightLine(
        ax_levelIce_weekly, [dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24], dateNum_reshape_hourly[(week+1)*constants.level_ice_statistic_days*24]], 
        level_ice_deepest_mode[week], {'color':'red', 'linestyle':'--'})
    ax_levelIce_weekly, line_LI_Dm_expect_weekly = initialize_plot_straightLine(
        ax_levelIce_weekly, [dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24], dateNum_reshape_hourly[(week+1)*constants.level_ice_statistic_days*24]], 
        level_ice_expect_deepest_mode[week], {'color':'olive', 'linestyle':'--'})
    currentDayPatch = mpatches.Rectangle((dateNum[newDayIndex[week*constants.level_ice_statistic_days]], 0), 1, 30, edgecolor='None', facecolor='green', alpha=0.3, zorder=4)
    line_levelIce_weekly_currentDayPatch = ax_levelIce_weekly.add_patch(currentDayPatch)
    ax_levelIce_weekly.invert_yaxis() # make the y-axis upside down, since it is the ice depth plotted


    ### plot daily level ice thickness
    ax_levelIce_daily = figure_LI_statistics.add_subplot(gridspec_LI_statistics[6:8, 0:3])
    ax_levelIce_daily.set_title(f"Daily LI draft {dateTicks_days[week*constants.level_ice_statistic_days+day]}")
    ax_levelIce_daily.set_xlabel('Time')
    ax_levelIce_daily.set_ylabel('Ice draft [m]')
    ax_levelIce_daily, line_draftLI_daily = initialize_plot_draft(
        ax_levelIce_daily, 
        np.concatenate(dateNum_reshape_hourly[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day]), 
        np.concatenate(draft_reshape_hourly[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day]), 
        {'color':'blue', 'linewidth':0.5}, ylim=[-0.1, 5.1],
        x_ticks=dateNum[newHourIndex[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day][1::4]], 
        x_ticklabels=dateTicks_hours[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day][1::4])
    currentHourPatch = mpatches.Rectangle(
        (dateNum[newHourIndex[week*constants.level_ice_statistic_days*constants.hours_day +day*constants.hours_day]], 0), 1/24, 30, 
        edgecolor='None', facecolor='blue', alpha=0.3, zorder=4)
    line_levelIce_daily_currentHourPatch = ax_levelIce_daily.add_patch(currentHourPatch)
    ax_levelIce_daily.invert_yaxis() # make the y-axis upside down, since it is the ice depth plotted


    ### reserve the space for the legend at grid position (3,2)
    h, l = ax_iceDraft_overview.get_legend_handles_labels() 
    ax_legend_patches = figure_LI_statistics.add_subplot(gridspec_LI_statistics[6:8, 3:4])
    ax_legend_patches.axis('off')
    ax_legend_patches.add_patch(mpatches.Rectangle((0, 0), 0, 0, edgecolor='None', facecolor='red', alpha=0.3, zorder=4, label='Selected week'))
    ax_legend_patches.add_patch(mpatches.Rectangle((0, 0), 0, 0, edgecolor='None', facecolor='green', alpha=0.3, zorder=4, label='Selected day'))
    ax_legend_patches.add_patch(mpatches.Rectangle((0, 0), 0, 0, edgecolor='None', facecolor='blue', alpha=0.3, zorder=4, label='Selected hour'))
    h_patches, l_patches = ax_legend_patches.get_legend_handles_labels()
    ax_legend_patches.legend(h+h_patches, l+l_patches)


    while True:
        # loop through the weeks
        print("Press 'f' for next WEEK, 'd' for this week and 's' for last week and 'x' to exit the program. You can also enter the week directly. In all cases, press enter afterwards.")
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
        ax_levelIce_mode_weekly, line_dist_levelIce_mode_weekly = update_plot_distribution(
            ax_levelIce_mode_weekly, line_dist_levelIce_mode_weekly, 
            np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), interpolated_histBins_array)
        currentPoint_marker = update_plot_spectrum(ax_iceDraft_spectrum, currentPoint_marker, dateNum_hist_levelIce_weekly[week], level_ice_deepest_mode[week])
        currentWeekPatch.set_xy([dateNum[newDayIndex[week*constants.level_ice_statistic_days]], 0])
        ax_levelIce_weekly, line_draftLI_weekly = plot_draft(
            ax_levelIce_weekly, line_draftLI_weekly, np.concatenate(dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
            np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
            x_ticks=dateNum[newDayIndex[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days:2]], 
            x_ticklabels=dateTicks_days[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days:2])
        ax_levelIce_weekly, line_LI_DM_weekly = plot_straightLine(
            ax_levelIce_weekly, line_LI_DM_weekly, 
            [dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24][0], dateNum_reshape_hourly[(week+1)*constants.level_ice_statistic_days*24][0]], 
            level_ice_deepest_mode[week])
        ax_levelIce_weekly, line_LI_Dm_expect_weekly = plot_straightLine(
            ax_levelIce_weekly, line_LI_Dm_expect_weekly, 
            [dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24][0], dateNum_reshape_hourly[(week+1)*constants.level_ice_statistic_days*24][0]], 
            level_ice_expect_deepest_mode[week])
        currentDayPatch.set_xy([dateNum[newDayIndex[week*constants.level_ice_statistic_days]], 0])
        
        day = 0
        ax_levelIce_daily.set_title(f"Daily LI draft {dateTicks_days[week*constants.level_ice_statistic_days+day]}")
        while True:
            # loop through the days of the week
            print("Press 'f' for next DAY, 'd' for this day and 's' for last day and 'x' to exit the program. You can also enter the day directly. In all cases, press enter afterwards.")
            success, day = user_input_iteration.get_user_input_iteration(day, constants.level_ice_statistic_days+1) 
            # allow one day more than the level_ice_statistic_days, since the first and last day are half days both, otherwise, it would break before the week is over
            if success == -1:
                break
            elif success == 0:
                continue
            elif success == 1:
                pass
            else:
                raise ValueError("Invalid success value.")
            currentDayPatch.set_xy([dateNum[newDayIndex[week*constants.level_ice_statistic_days + day]], 0])
            # currentHourPatch.set_xy([dateNum[newHourIndex[week*constants.level_ice_statistic_days*constants.hours_day +day*constants.hours_day]], 0])
            nearest_hourStart = np.argmin([np.abs(dateNum[newDayIndex[week*constants.level_ice_statistic_days + day]] - dateNum_hour[0]) for dateNum_hour in dateNum_reshape_hourly])
            ax_levelIce_daily.set_title(f"Daily LI draft {dateTicks_days[week*constants.level_ice_statistic_days+day]}")
            ax_levelIce_daily, line_draftLI_daily = plot_draft(
                ax_levelIce_daily, line_draftLI_daily, 
                np.concatenate(dateNum_reshape_hourly[nearest_hourStart:nearest_hourStart + constants.hours_day]), 
                np.concatenate(draft_reshape_hourly[nearest_hourStart:nearest_hourStart + constants.hours_day]), 
                x_ticks=dateNum[newHourIndex[nearest_hourStart:nearest_hourStart + constants.hours_day][1::4]], 
                x_ticklabels=dateTicks_hours[nearest_hourStart:nearest_hourStart + constants.hours_day][1::4])

    print('done')


def initialize_plot_straightLine(fig, row, col, x, y, line_properties={}):
    """Plot a straight line on the axis ax with constant y value
    """
    straightLine = go.Scatter(
        x=x,
        y=np.ones(len(x)) * y,
        mode='lines',
        line=dict(color=line_properties.get('color', 'red'), width=line_properties.get('linewidth', 1)),
        name='Straight Line'
    )
    fig.add_trace(straightLine, row=row, col=col)
    return fig, straightLine

def plot_straightLine(fig, straightLine, x, y):
    """Plot a straight line on the axis ax with constant y value
    """
    straightLine.x = x
    straightLine.y = np.ones(len(x)) * y
    return fig, straightLine

def initialize_plot_draft(fig, row, col, dateNum_data, draft_data, draft_properties={}, xlim=None, ylim=None, x_ticks=None, x_ticklabels=None):
    """Plot the draft data on the axis ax with the properties specified in draft_properties
    """
    draft_line = go.Scatter(
        x=dateNum_data,
        y=draft_data,
        mode='lines',
        line=dict(color=draft_properties.get('color', 'blue'), width=draft_properties.get('linewidth', 1)),
        name='Draft Line'
    )
    fig.add_trace(draft_line, row=row, col=col)
    fig.update_xaxes(range=xlim, row=row, col=col)
    fig.update_yaxes(range=ylim, row=row, col=col)
    if x_ticks is not None:
        fig.update_xaxes(tickvals=x_ticks, ticktext=x_ticklabels, row=row, col=col)
    return fig, draft_line

def plot_draft(fig, draft_line, dateNum_data, draft_data, x_ticks=None, x_ticklabels=None):
    """Plot the draft data on the axis ax with the properties specified in draft_properties
    """
    draft_line.x = dateNum_data
    draft_line.y = draft_data
    if x_ticks is not None:
        fig.update_xaxes(tickvals=x_ticks, ticktext=x_ticklabels)
    return fig, draft_line

def initialize_plot_histogram(fig, row, col, hist_data, hist_properties, hist_points=None, xlim=None, ylim=None):
    """Plot a histogram of the data in hist_data on the axis ax with the properties specified in hist_properties
    """
    if hist_points is not None:
        hist_heights = hist_data
    else:
        hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=hist_properties.get('density', False))
        hist_heights = hist_numpy[0]
        hist_points = hist_numpy[1]
    hist_line = go.Bar(
        x=hist_points[:-1],
        y=hist_heights,
        marker=dict(color=hist_properties.get('color', 'blue'), opacity=hist_properties.get('alpha', 0.5)),
        name='Histogram'
    )
    fig.add_trace(hist_line, row=row, col=col)
    fig.update_xaxes(range=xlim, row=row, col=col)
    fig.update_yaxes(range=ylim, row=row, col=col)
    return fig, hist_line

def plot_histogram(fig, hist_line, hist_data, hist_properties={}):
    """Plot a histogram of the data in hist_data on the axis ax with the properties specified in hist_properties
    """
    if not hist_properties == {}:
        hist_data, _ = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=hist_properties.get('density', False))
    hist_line.y = hist_data
    return fig, hist_line

def initialize_plot_distribution(fig, row, col, hist_data, line_x, dist_properties={}):
    """Plot a distribution of the data in dist_data on the axis ax fitting for the line_x values on already initialited axis ax
    """
    kde = scipy.stats.gaussian_kde(hist_data, bw_method=0.1)
    line_y = kde(line_x)
    dist_line = go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line=dict(color=dist_properties.get('color', 'red')),
        name='Distribution Line'
    )
    fig.add_trace(dist_line, row=row, col=col)
    return fig, dist_line

def update_plot_distribution(fig, dist_line, hist_data, line_x):
    """Update the line of the distirbtion of the data in hist_data on the axis ax
    """
    kde = scipy.stats.gaussian_kde(hist_data, bw_method=0.1)
    line_y = kde(line_x)
    dist_line.y = line_y
    return fig, dist_line

def plot_spectrum(fig, colorMesh, scatter1_line, scatter2_line, CP, spec_x, spec_y, spec_z, spec_properties, scatter1_x, scatter1_y, scatter2_x, scatter2_y, currentPoint_x, currentPoint_y, row, col):
    """
    Plot a spectrum of the data in x and y on the axis ax with the properties specified in spectrum_properties
    """
    # Update color mesh
    colorMesh.x = spec_x
    colorMesh.y = spec_y
    colorMesh.z = spec_z
    colorMesh.showscale = spec_properties.get('showscale', True)
    colorMesh.colorscale = spec_properties.get('colorscale', 'Viridis')

    # Update scatter plots
    scatter1_line.x = scatter1_x
    scatter1_line.y = scatter1_y
    scatter2_line.x = scatter2_x
    scatter2_line.y = scatter2_y

    # Update current point
    CP.x = [currentPoint_x]
    CP.y = [currentPoint_y]

    # Add traces to figure
    fig.add_trace(colorMesh, row=row, col=col)
    fig.add_trace(scatter1_line, row=row, col=col)
    fig.add_trace(scatter2_line, row=row, col=col)
    fig.add_trace(CP, row=row, col=col)

    return fig, colorMesh, scatter1_line, scatter2_line, CP


def initialize_plot_spectrum(fig, row, col, spec_x, spec_y, spec_z, spec_properties, scatter1_x, scatter1_y, scatter1_properties, scatter2_x, scatter2_y, scatter2_properties, currentPoint_x, currentPoint_y, xlim=None, ylim=None, xticks=None, xTitle=None, yTitle=None, title=None):
    """Initialize the spectrum plot with the given data and properties
    """
    colorMesh = go.Heatmap(
        x=spec_x,
        y=spec_y,
        z=spec_z,
        colorscale=spec_properties.get('colorscale', 'Viridis'),
        name='Spectrum'
    )
    scatter1_line = go.Scatter(
        x=scatter1_x,
        y=scatter1_y,
        mode='markers',
        marker=dict(color=scatter1_properties.get('color', 'red'), size=scatter1_properties.get('size', 10), symbol=scatter1_properties.get('marker', 'circle')),
        name='Scatter 1'
    )
    scatter2_line = go.Scatter(
        x=scatter2_x,
        y=scatter2_y,
        mode='markers',
        marker=dict(color=scatter2_properties.get('color', 'olive'), size=scatter2_properties.get('size', 10), symbol=scatter2_properties.get('marker', 'triangle-up')),
        name='Scatter 2'
    )
    current_point = go.Scatter(
        x=[currentPoint_x],
        y=[currentPoint_y],
        mode='markers',
        marker=dict(color='red', size=12, symbol='square'),
        name='Current Point'
    )
    fig.add_trace(colorMesh, row=row, col=col)
    fig.add_trace(scatter1_line, row=row, col=col)
    fig.add_trace(scatter2_line, row=row, col=col)
    fig.add_trace(current_point, row=row, col=col)
    fig.update_xaxes(range=xlim, tickvals=xticks, row=row, col=col)
    fig.update_yaxes(range=ylim, row=row, col=col)
    # set the x-axis title
    fig.update_xaxes(title_text=xTitle, row=row, col=col)
    # set the y-axis title
    fig.update_yaxes(title_text=yTitle, row=row, col=col)
    # set the figure title
    fig.update_layout(title_text=title)
    return fig, colorMesh, scatter1_line, scatter2_line, current_point

def update_plot_spectrum(fig, colorMesh, scatter1_line, scatter2_line, current_point, spec_x, spec_y, spec_z, scatter1_x, scatter1_y, scatter2_x, scatter2_y, currentPoint_x, currentPoint_y):
    """Update the spectrum plot with the given data
    """
    colorMesh.x = spec_x
    colorMesh.y = spec_y
    colorMesh.z = spec_z
    scatter1_line.x = scatter1_x
    scatter1_line.y = scatter1_y
    scatter2_line.x = scatter2_x
    scatter2_line.y = scatter2_y
    current_point.x = [currentPoint_x]
    current_point.y = [currentPoint_y]
    return fig, colorMesh, scatter1_line, scatter2_line, current_point
