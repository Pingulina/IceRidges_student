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
myColor = import_module('myColor', 'helper_functions')
data_analysis_plot_plotly_initialize = import_module('data_analysis_plot_plotly_initialize', 'plot_functions')



def level_ice_statistics_initialize(year, loc, week, dict_ridge_statistics_allYears, dict_ridge_statistics_jsonified):
    """Analysing the level ice data, determine the level ice mode for each week
    """
    ### get the variables out of the dicts
    all_LIDM = dict_ridge_statistics_allYears['all_LIDM']
    all_MKD = dict_ridge_statistics_allYears['all_MKD']
    all_Dmax = dict_ridge_statistics_allYears['all_Dmax']
    all_number_of_ridges = dict_ridge_statistics_allYears['all_number_of_ridges']

    print(dict_ridge_statistics_jsonified.keys())
    dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified) # this is to convert the jsonified data to a dict with its original data types
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
    mean_dateNum = dict_ridge_statistics['mean_dateNum']
    mean_keel_draft = dict_ridge_statistics['mean_keel_draft']
    level_ice_deepest_mode = dict_ridge_statistics['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics['level_ice_expect_deepest_mode']
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
            [{"colspan": 3, "rowspan":2}, None, None, {"colspan": 3, "rowspan":2}, None, None],
            [None, None, None, None, None, None],
            [{"colspan": 3}, None, None, {"colspan": 1, "rowspan":2}, {"colspan":1, "rowspan":2}, {"colspan":1, "rowspan":2}],
            [{"colspan": 3}, None, None, None, None, None]
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
        fig=figure_LI_statistics, row=1, col=4, spec_x=dateNum_hist_levelIce_weekly, spec_y=histBins_mids, spec_z=hist_levelIce_mode_weekly_plot.T, spec_properties={}, 
        scatter1_x=dateNum_hist_draft_weekly, scatter1_y=level_ice_deepest_mode, scatter1_properties={}, 
        scatter2_x=dateNum_hist_levelIce_weekly, scatter2_y=level_ice_expect_deepest_mode, scatter2_properties={}, 
        currentPoint_x=dateNum_hist_levelIce_weekly[0], currentPoint_y=level_ice_deepest_mode[0], ylim=[0, 3], xticks_text=dateTicks, xticks=dateNum[newMonthIndex[::2]],
        xTitle='Date', yTitle='Level ice draft [m]', title='Level ice draft spectrum')
    
    # figure_LI_statistics, colorMesh_iceDraft_spectrum, heatmap_patch_trace_index, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker = data_analysis_plot_plotly_initialize.initialize_plot_spectrum(
    #     figure_LI_statistics, row=3, col=1, 
    #     HHi_plot=hist_levelIce_mode_weekly_plot, X_spectogram=X, Y_spectogram=Y,
    #     # HHi_plot=np.zeros((len(dateNum_rc_pd), len(deepest_mode_weekly)), dtype=float), X_spectogram=np.arange(len(dateNum_rc_pd)), Y_spectogram=np.arange(len(deepest_mode_weekly)),
    #     time=dateNum_reshape, draft=draft, time_mean=dateNum_rc_pd, LI_deepestMode=deepest_mode_weekly, 
    #     LI_deepestMode_expect=deepest_mode_expect_weekly, week_starts=week_starts, week_ends=week_ends, 
    #     week=week, xlabel='Date specto', ylabel='Draft [m]', xTickLabels=dateNum[newMonthIndex[::2]])
    
    # figure_LI_statistics, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker = plot_spectrum(
    #     figure_LI_statistics, 1, 4, colorMesh_iceDraft_spectrum, scatter_iceDraft, scatter_iceDraft_expect, currentPoint_marker,
    #     X, Y, hist_levelIce_mode_weekly.T, {}, dateNum_hist_levelIce_weekly, level_ice_deepest_mode, 
    #     dateNum_hist_levelIce_weekly, level_ice_expect_deepest_mode, dateNum_hist_levelIce_weekly[0], level_ice_deepest_mode[0]
    # )


    # ice draft overview
    
    figure_LI_statistics, line_iceDraft_traceIndex, line_LI_iceDraft_traceIndex, line_LIDM_traceIndex, line_iceDraft_traceIndex, patch_current_week_traceIndex = initialize_iceDraft_overview(
        figure_LI_statistics, row=1, col=1, dateNum=dateNum[0:-1:20], draft=draft[0:-1:20], prop_draft={'color':myColor.dark_blue(1), 'linewidth':0.5, 'label':'Ice draft'}, 
        dateNum_LI=dateNum_LI, draft_LI=draft_LI, prop_LI={'color':myColor.orange(1), 'linewidth':0.5, 'label':'Level ice draft'}, 
        dateNum_LIDM = dateNum_LI, draft_LIDM=level_ice_deepest_mode_hourly, prop_LIDM={'color':myColor.dark_red(1), 'linewidth':0.5, 'label':'Level ice deepest mode'},
        dateNum_expLIDM=dateNum_hist_levelIce_weekly, draft_expLIDM=level_ice_expect_deepest_mode, prop_expLIDM={'color':'olive', 'linewidth':0.5, 'label':'LI expected deepest mode'},
        week_starts=week_starts, week_ends=week_ends, week=week, xlabel='Date', ylabel='Ice draft [m]', xTickLabels=dateTicks, xTickIndices=newMonthIndex[::2], legend=True, title='Ice draft overview',
        currentPatchColor=myColor.dark_red(0.2)
        )
    
    ### level ice mode of the whole season
    # initialize the line indicating the current mode and the histogram of the level ice mode
    figure_LI_statistics, hist_levelIce_mode_traceIndex, line_hist_levelIce_mode_traceIndex = initialize_plot_histogram_line(
        figure_LI_statistics, row=3, col=4, line_x=[0, 0], line_y=[0, 12], line_properties={'color':myColor.dark_red(1), 'linestyle':'--', 'name':'current mode'},
        hist_data=level_ice_deepest_mode, hist_properties={'bins': histBins_array, 'density':True}, title='Level ice mode', xlabel='Ice draft [m]', ylabel='Density [-]', xlim=[-0.1, 8], ylim=[0, 4])
    
    ### level ice mode weekly
    kde = scipy.stats.gaussian_kde(np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), bw_method=0.1)
    line_x = np.linspace(histBins_array[0], histBins_array[-1], len(histBins_array)*4) #np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24])
    line_y = kde(line_x)
    figure_LI_statistics, hist_levelIce_mode_weekly_traceIndex, line_hist_levelIce_mode_weekly_traceIndex = initialize_plot_histogram_line(
        figure_LI_statistics, row=3, col=5, line_x=line_x, line_y=line_y, line_properties={'color':myColor.dark_red(1), 'linestyle':'--', 'name':'current mode'},
        hist_data=hist_draft_mode_weekly_dens[week], hist_properties={'bins': histBins_array, 'density':True}, title='Weekly level ice mode', xlabel='Ice draft [m]', ylabel='Density [-]', xlim=[-0.1, 3.1], ylim=[0, 4.1])
    

    ### plot weekly level ice thickness
    day_starts = [week_starts[week] + i for i in range(7)]
    day_ends = [week_starts[week] + i for i in range(1, 8)]
    print("weekly level ice draft")
    dateNum_week_hourly = dateNum_reshape_hourly[:,0][week*24*7:(week+1)*24*7]
    draft_LI_week = draft_LI[week*24*7:(week+1)*24*7]
    draft_LIDM_week = level_ice_deepest_mode_hourly[week*24*7:(week+1)*24*7]
    figure_LI_statistics, line_iceDraft_weekly_traceIndex, line_LI_iceDraft_weekly_traceIndex, line_LIDM_weekly_traceIndex, line_iceDraft_weekly_traceIndex, patch_current_day_traceIndex = initialize_iceDraft_overview(
        figure_LI_statistics, row=3, col=1, dateNum=np.concatenate(dateNum_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), 
        draft=np.concatenate(draft_reshape_hourly[week*constants.level_ice_statistic_days*24:(week+1)*constants.level_ice_statistic_days*24]), prop_draft={'color':myColor.dark_blue(1), 'linewidth':0.5, 'label':'Ice draft'}, 
        dateNum_LI=dateNum_week_hourly, draft_LI=draft_LI[week*24*7:(week+1)*24*7], prop_LI={'color':myColor.orange(1), 'linewidth':1, 'label':'Level ice draft'}, 
        dateNum_LIDM=dateNum_week_hourly, draft_LIDM=level_ice_deepest_mode_hourly[week*24*7:(week+1)*24*7], prop_LIDM={'color':myColor.dark_red(1), 'linewidth':1, 'label':'Level ice deepest mode'},
        dateNum_expLIDM=[dateNum_week_hourly[0], dateNum_week_hourly[-1]], draft_expLIDM=[level_ice_expect_deepest_mode[week], level_ice_expect_deepest_mode[week]], prop_expLIDM={'color':'olive', 'linewidth':1, 'label':'LI expected deepest mode'},
        week_starts=day_ends, week_ends=day_starts, week=day, xlabel='Date', ylabel='Ice draft [m]', ylim=[-0.1, 5.1], 
        xTickLabels=dateTicks_days[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days+1][1::2], xTickIndices=newDayIndex[week*constants.level_ice_statistic_days:(week+1)*constants.level_ice_statistic_days+1][1::2], 
        legend=True, title='Weekly level ice draft', currentPatchColor=myColor.green(0.2)
        )


    ### plot daily level ice thickness
    figure_LI_statistics, line_iceDraft_daily_traceIndex, patch_current_hour_traceIndex = initialize_iceDraft_daily(
        figure_LI_statistics, row=4, col=1, dateNum=np.concatenate(dateNum_reshape_hourly[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day]), 
        draft=np.concatenate(draft_reshape_hourly[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day]), prop_draft={'color':myColor.dark_blue(1), 'linewidth':0.5, 'label':'Ice draft'}, 
        week_starts=week_starts, week_ends=week_ends, week=0, xlabel='Time', ylabel='Ice draft [m]', ylim=[-0.1, 5.1], 
        xTickLabels=dateTicks_hours[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day][1::4], xTickIndices=newHourIndex[(week*constants.level_ice_statistic_days +day) * constants.hours_day:(week*constants.level_ice_statistic_days +day+1) * constants.hours_day][1::4], 
        legend=True, title=f"Daily LI draft {dateTicks_days[week*constants.level_ice_statistic_days+day]}"
        )


    ### reserve the space for the legend at grid position (3,2)


    # Extract legend entries from the plot in row 2, column 1
    legend_entries = []
    for trace in figure_LI_statistics['data']:
        if trace['xaxis'] == 'x3' and trace['yaxis'] == 'y3':  # Check if the trace belongs to row 2, col 1
            legend_entries.append(go.Scatter(
                x=[None], y=[None],
                mode='markers',
                marker=dict(size=15, color=trace['line']['color'], symbol='square'),
                name=trace['name']
            ))

    # Create legend patches
    legend_patches = [
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=myColor.dark_red(1), symbol='square', opacity=0.3),
            name='Selected week'
        ),
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color='green', symbol='square', opacity=0.3),
            name='Selected day'
        ),
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=myColor.mid_blue(1), symbol='square', opacity=0.3),
            name='Selected hour'
        )
    ]

    # Add legend patches to the figure
    for patch in legend_patches + legend_entries:
        figure_LI_statistics.add_trace(patch, row=3, col=6)

    # Update layout to hide axes for the legend subplot
    figure_LI_statistics.update_xaxes(visible=False, row=3, col=5)
    figure_LI_statistics.update_yaxes(visible=False, row=3, col=5)

    dict_all_trace_indices = {
        'line_iceDraft_traceIndex': line_iceDraft_traceIndex,
        'line_LI_iceDraft_traceIndex': line_LI_iceDraft_traceIndex,
        'line_LIDM_traceIndex': line_LIDM_traceIndex,
        'line_iceDraft_traceIndex': line_iceDraft_traceIndex,
        'patch_current_week_traceIndex': patch_current_week_traceIndex,
        'line_iceDraft_weekly_traceIndex': line_iceDraft_weekly_traceIndex,
        'line_LI_iceDraft_weekly_traceIndex': line_LI_iceDraft_weekly_traceIndex,
        'line_LIDM_weekly_traceIndex': line_LIDM_weekly_traceIndex,
        'line_iceDraft_weekly_traceIndex': line_iceDraft_weekly_traceIndex,
        'patch_current_day_traceIndex': patch_current_day_traceIndex,
        'line_iceDraft_daily_traceIndex': line_iceDraft_daily_traceIndex,
        'patch_current_hour_traceIndex': patch_current_hour_traceIndex,
        'line_iceDraft_daily_traceIndex': line_iceDraft_daily_traceIndex,
        'line_hist_levelIce_mode_weekly_traceIndex': line_hist_levelIce_mode_weekly_traceIndex,
        'line_hist_levelIce_mode_traceIndex': line_hist_levelIce_mode_traceIndex,
        'line_iceDraft_weekly_currentDayPatch_traceIndex': patch_current_day_traceIndex,
        'line_iceDraft_daily_currentHourPatch_traceIndex': patch_current_hour_traceIndex,
        'scatter_iceDraft_traceIndex': scatter_iceDraft,
        'scatter_iceDraft_expect_traceIndex': scatter_iceDraft_expect,
        'currentPoint_marker_traceIndex': currentPoint_marker,
        'colorMesh_iceDraft_spectrum_traceIndex': colorMesh_iceDraft_spectrum
    }
    this_time = dateNum_rc_pd[week]
    this_draft = deepest_mode_weekly[week]

    return figure_LI_statistics, dict_all_trace_indices, this_time, this_draft


def level_ice_statistics_update(figure_LI_statistics, year, loc, week, dict_ridge_statistics_allYears, dict_ridge_statistics_jsonified):

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
        line=dict(color=line_properties.get('color', myColor.dark_red(1)), width=line_properties.get('linewidth', 1)),
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

def initialize_iceDraft_overview(
        fig, row, col, dateNum, draft, prop_draft, dateNum_LI, draft_LI, prop_LI, dateNum_LIDM, draft_LIDM, prop_LIDM,
        dateNum_expLIDM, draft_expLIDM, prop_expLIDM, week_starts, week_ends, week, currentPatchColor=myColor.mid_blue(0.4), xlabel=None, ylabel=None, xlim=None, ylim=None, 
        xTickLabels=None, xTickIndices=None, legend=False, title=None
        ):
    if xlabel is None:
        xlabel = ''
    if ylabel is None:
        ylabel = ''
    if xlim is None:
        xlim = [dateNum[0], dateNum[-1]]
    if ylim is None:
        ylim = [min(draft), max(draft)]


    # define the patch first, so that the lines are on top of the patch
    patch_current_week = go.Scatter(
        x=[week_starts[week], week_ends[week], week_ends[week], week_starts[week], week_starts[week]],
        y=[0, 0, max(draft), max(draft), 0],
        fill='toself',
        fillcolor=currentPatchColor,
        # line=dict(color=currentPatchColor),
        name='Current week ice data',
        mode='lines',
        showlegend=legend
    )
    # define all lines
    line_draft = go.Scatter(
        x=dateNum,
        y=draft,
        mode='lines',
        line=dict(color=prop_draft.get('color', myColor.dark_blue(1)), width=prop_draft.get('linewidth', 1)),
        name=prop_draft.get('label', '-'),
        showlegend=legend
    )
    line_draft_LI = go.Scatter(
        x=dateNum_LI,
        y=draft_LI,
        mode='lines',
        line=dict(color=prop_LI.get('color', myColor.orange(1)), width=prop_LI.get('linewidth', 1)),
        name=prop_LI.get('label', '-'),
        showlegend=legend
    )
    line_draft_LIDM = go.Scatter(
        x=dateNum_LIDM,
        y=draft_LIDM,
        mode='lines',
        line=dict(color=prop_LIDM.get('color', myColor.dark_red(1)), width=prop_LIDM.get('linewidth', 1)),
        name=prop_LIDM.get('label', '-'),
        showlegend=legend
    )
    line_draft_expLIDM = go.Scatter(
        x=dateNum_expLIDM,
        y=draft_expLIDM,
        mode='lines',
        line=dict(color=prop_expLIDM.get('color', 'olive'), width=prop_expLIDM.get('linewidth', 1)),
        name=prop_expLIDM.get('label', '-'),
        showlegend=legend
    )

    fig.add_trace(line_draft, row=row, col=col)
    line_iceDraft_traceIndex = len(fig.data) - 1
    fig.add_trace(line_draft_LI, row=row, col=col)
    line_LI_iceDraft_traceIndex = len(fig.data) - 1
    fig.add_trace(line_draft_LIDM, row=row, col=col)
    line_LIDM_traceIndex = len(fig.data) - 1
    fig.add_trace(line_draft_expLIDM, row=row, col=col)
    line_expLIDM_traceIndex = len(fig.data) - 1
    fig.add_trace(patch_current_week, row=row, col=col)
    patch_current_week_traceIndex = len(fig.data) - 1

    if xTickLabels is not None:
        if xTickIndices is not None:
            dateNum_every_day = dateNum[xTickIndices]
        else:
            dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0] + 1]
        tickvals = dateNum_every_day[::50]
        ticktext = xTickLabels[::50] if xTickLabels is not None else None
        
        fig.update_xaxes(
            tickvals=tickvals,
            ticktext=ticktext,
            row=row, col=col,
            automargin=True,
            range=[xlim[0], xlim[1]],
            title_text=xlabel
        )
    else:
        fig.update_xaxes(
            row=row, col=col,
            automargin=True,
            range=[xlim[0], xlim[1]],
            title_text=xlabel
        )

    fig.update_yaxes(
        row=row, col=col,
        automargin=True,
        range=[ylim[1], ylim[0]],
        title_text=ylabel,
        # autorange='reversed'
        )
    if title is not None:
        fig.update_layout(title_text=title)
    return fig, line_iceDraft_traceIndex, line_LI_iceDraft_traceIndex, line_LIDM_traceIndex, line_expLIDM_traceIndex, patch_current_week_traceIndex

def initialize_iceDraft_daily(
        fig, row, col, dateNum, draft, prop_draft, week_starts, week_ends, week, xlabel=None, ylabel=None, xlim=None, ylim=None, 
        xTickLabels=None, xTickIndices=None, legend=False, title=None
        ):
    if xlabel is None:
        xlabel = ''
    if ylabel is None:
        ylabel = ''
    if xlim is None:
        xlim = [dateNum[0], dateNum[-1]]
    if ylim is None:
        ylim = [min(draft), max(draft)]
    patch_current_week = go.Scatter(
        x=[week_starts[week], week_ends[week], week_ends[week], week_starts[week], week_starts[week]],
        y=[0, 0, max(draft), max(draft), 0],
        fill='toself',
        fillcolor=myColor.mid_blue(0.4),
        line=dict(color=myColor.mid_blue(0.4)),
        name='Current week ice data',
        mode='lines',
        showlegend=legend
    )
    line_draft = go.Scatter(
        x=dateNum,
        y=draft,
        mode='lines',
        line=dict(color=prop_draft.get('color', myColor.dark_red(1)), width=prop_draft.get('linewidth', 1)),
        name=prop_draft.get('label', '-'),
        showlegend=legend
    )

    fig.add_trace(line_draft, row=row, col=col)
    line_iceDraft_traceIndex = len(fig.data) - 1
    fig.add_trace(patch_current_week, row=row, col=col)
    patch_current_week_traceIndex = len(fig.data) - 1

    if xTickLabels is not None:
        if xTickIndices is not None:
            dateNum_every_day = dateNum[xTickIndices]
        else:
            dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0] + 1]
        tickvals = dateNum_every_day[::50]
        ticktext = xTickLabels[::50] if xTickLabels is not None else None
        
        fig.update_xaxes(
            tickvals=tickvals,
            ticktext=ticktext,
            row=row, col=col,
            automargin=True,
            range=[xlim[0], xlim[1]],
            title_text=xlabel
        )
    else:
        fig.update_xaxes(
            row=row, col=col,
            automargin=True,
            range=[xlim[0], xlim[1]],
            title_text=xlabel
        )

    fig.update_yaxes(
        row=row, col=col,
        automargin=True,
        range=[ylim[1], ylim[0]],
        title_text=ylabel,
        # autorange='reversed'
        )
    if title is not None:
        fig.update_layout(title_text=title)
    return fig, line_iceDraft_traceIndex, patch_current_week_traceIndex

def initialize_plot_draft(fig, row, col, dateNum_data, draft_data, draft_properties={}, xlim=None, ylim=None, x_ticks=None, x_ticklabels=None):
    """Plot the draft data on the axis ax with the properties specified in draft_properties
    """
    draft_line = go.Scatter(
        x=dateNum_data,
        y=draft_data,
        mode='lines',
        line=dict(color=draft_properties.get('color', myColor.dark_blue(1)), width=draft_properties.get('linewidth', 1)),
        name='Draft Line'
    )
    fig.add_trace(draft_line, row=row, col=col)
    fig.update_xaxes(range=xlim, row=row, col=col)
    fig.update_yaxes(range=ylim, row=row, col=col)
    trace_index = len(fig.data) - 1
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

def initialize_plot_histogram_line(fig, row, col, line_x, line_y, line_properties, hist_data, hist_properties, hist_points=None, xlim=None, ylim=None, xlabel=None, ylabel=None, title=None):
    """Plot a line of the data in line_x and line_y combinded with a histogram of the data in hist_data on the axis ax with the properties specified in hist_properties"""
    if hist_points is not None:
        hist_heights = hist_data
    else:
        hist_numpy = np.histogram(hist_data, bins=hist_properties.get('bins', 10), density=hist_properties.get('density', False))
        hist_heights = hist_numpy[0]
        hist_points = hist_numpy[1]
    hist_line = go.Bar(
        x=hist_points[:-1],
        y=hist_heights,
        marker=dict(color=hist_properties.get('color', myColor.dark_red(1)), opacity=hist_properties.get('alpha', 0.5)),
        name='Histogram'
    )
    fig.add_trace(hist_line, row=row, col=col)
    hist_trace_index = len(fig.data) - 1
    line_trace = go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line=dict(color=line_properties.get('color', myColor.dark_red(1)), width=line_properties.get('linewidth', 1)),
        name='Line'
    )
    fig.add_trace(line_trace, row=row, col=col)
    line_trace_index = len(fig.data) - 1
    # Update x-axis
    fig.update_xaxes(range=xlim, row=row, col=col, title_text=xlabel)
    # Update y-axis
    fig.update_yaxes(range=ylim, row=row, col=col, title_text=ylabel)
    # Update title
    if title is not None:
        fig.update_layout(title_text=title)
    return fig, hist_trace_index, line_trace_index

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
        marker=dict(color=hist_properties.get('color', myColor.mid_blue(1)), opacity=hist_properties.get('alpha', 0.5)),
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
        line=dict(color=dist_properties.get('color', myColor.dark_red(1))),
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

def plot_spectrum(fig, row, col, colorMesh, scatter1_line, scatter2_line, CP, spec_x, spec_y, spec_z, spec_properties, scatter1_x, scatter1_y, scatter2_x, scatter2_y, currentPoint_x, currentPoint_y):
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

    return fig, colorMesh, scatter1_line, scatter2_line, CP


def initialize_plot_spectrum(fig, row, col, spec_x, spec_y, spec_z, spec_properties, scatter1_x, scatter1_y, scatter1_properties, scatter2_x, scatter2_y, scatter2_properties, currentPoint_x, currentPoint_y, xlim=None, ylim=None, xticks=None, xticks_text=None, xTitle=None, yTitle=None, title=None):
    """Initialize the spectrum plot with the given data and properties
    """
    print(f"xticks: {xticks}")
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
        marker=dict(color=scatter1_properties.get('color', myColor.dark_red(1)), size=scatter1_properties.get('size', 10), symbol=scatter1_properties.get('marker', 'circle')),
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
        marker=dict(color=myColor.dark_red(1), size=12, symbol='square'),
        name='Current Point'
    )
    fig.add_trace(colorMesh, row=row, col=col)
    fig.add_trace(scatter1_line, row=row, col=col)
    fig.add_trace(scatter2_line, row=row, col=col)
    fig.add_trace(current_point, row=row, col=col)

    if xlim is None:
        spec_x_diff = np.mean(np.diff(spec_x))
        xlim = [spec_x[0]-spec_x_diff/2, spec_x[-1]+spec_x_diff/2]
    if ylim is None:
        ylim = [spec_y[0], spec_y[-1]]
    if xTitle is None:
        xTitle = ''
    if yTitle is None:
        yTitle = ''
    

    if xticks is not None:
        # set the x-axis title
        fig.update_xaxes(range=xlim, tickvals=xticks, ticktext=xticks_text, title_text=xTitle, row=row, col=col)
    else:
        # set the x-axis title
        fig.update_xaxes(range=xlim, title_text=xTitle, row=row, col=col)
    # set the y-axis title
    fig.update_yaxes(range=ylim, title_text=yTitle, row=row, col=col)
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
