import plotly.graph_objects as go
import numpy as np
import os
import sys
import scipy.stats

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module

myColor = import_module('myColor', 'helper_functions')


def update_current_week_patch(fig, trace_index, week_starts, week_ends, week, ylim=None):
    """
    Update the current week patch in the figure.

    Parameters:
    - fig: The Plotly figure object.
    - trace_index: The index of the current week patch trace in the figure.
    - week_starts: List of start times for each week.
    - week_ends: List of end times for each week.
    - week: The current week index.
    - ylim: The y-axis limits.
    """
    # print('fig: ', fig)
    fig['data'][trace_index]['x'] = [week_starts[week], week_ends[week], week_ends[week], week_starts[week]]
    if ylim is not None:
        fig['data'][trace_index]['y'] = [ylim[0], ylim[0], ylim[1], ylim[1]]

    return fig

def update_plot_weekly_data_draft(
        fig, draftThis_trace_index, draftThis_peaks_trace_index, draftThis_LIdraft_e_trace_index, time, draft, time_ridge, draft_ridge, 
        time_LI, draft_LI, week, xTickLabels=None, row=1, col=2, dateTickDistance=1):

    # Convert time to np.array
    time = np.array(time)
    dateNum_every_day = time[week][np.where(np.diff(time[week].astype(int)))[0] + 1]

    # Update the Raw ULS draft signal line plot
    fig['data'][draftThis_trace_index]['x'] = time[week]
    fig['data'][draftThis_trace_index]['y'] = draft[week]

    # Update the Individual ridge peaks scatter plot
    fig['data'][draftThis_peaks_trace_index]['x'] = time_ridge[week]
    fig['data'][draftThis_peaks_trace_index]['y'] = draft_ridge[week]

    # Update the Level ice draft estimate step plot
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    keel_dateNum_weekEnd = [date[-1] for date in time_LI]
    fig['data'][draftThis_LIdraft_e_trace_index]['x'] = [time_LI[week][0], time_LI[week][-1]] # [keel_dateNum_weekStart[week], keel_dateNum_weekEnd[week]]
    fig['data'][draftThis_LIdraft_e_trace_index]['y'] = [draft_LI[week], draft_LI[week]]

    # Update the x-axis ticks and labels
    tickvals = dateNum_every_day[:7:dateTickDistance]
    ticktext = xTickLabels[week*7:(week+1)*7:dateTickDistance] if xTickLabels is not None else None
    print('fig keys: ', fig['layout']['xaxis2'].keys())
    fig['layout']['xaxis3'].update(
        range=[time[week][0], time[week][-1]],
        tickvals=tickvals,
        ticktext=ticktext,
    )

    return fig


def update_plot_spectrum(fig, heatmap_patch_trace_index, heatmap_marker_trace_index, time_mean, LI_deepestMode, week_starts, week_ends, week):
    fig['data'][heatmap_patch_trace_index]['x'] = [week_starts[week], week_ends[week], week_ends[week], week_starts[week], week_starts[week]]
    lrs1x = (time_mean[-1] - time_mean[0]) / 20
    lrs1y = 4 / 20
    x_left = time_mean[week] - lrs1x / 2
    x_right = time_mean[week] + lrs1x / 2
    y_bottom = LI_deepestMode[week] - lrs1y / 2
    y_top = LI_deepestMode[week] + lrs1y / 2
    fig['data'][heatmap_marker_trace_index]['x'] = [x_left, x_right, x_right, x_left, x_left]
    fig['data'][heatmap_marker_trace_index]['y'] = [y_bottom, y_bottom, y_top, y_top, y_bottom]
    
    return fig


def update_plot_weekly_data_scatter_marker(fig, current_week_marker_trace_index, xData_all, yData_all, xData_thisYear, yData_thisYear, week):
    lrs1x = (max(xData_all) - min(xData_all)) / 40
    lrs1y = (max(yData_all) - min(yData_all)) / 20
    x_left = xData_thisYear[week] - lrs1x / 2
    x_right = xData_thisYear[week] + lrs1x / 2
    y_bottom = yData_thisYear[week] - lrs1y / 2
    y_top = yData_thisYear[week] + lrs1y / 2
    fig['data'][current_week_marker_trace_index]['x'] = [x_left, x_right, x_right, x_left, x_left],
    fig['data'][current_week_marker_trace_index]['x'] = [y_bottom, y_bottom, y_top, y_top, y_bottom],
    
    return fig