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


def initialize_plot_data_draft(fig, row, col, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, week_starts, week_ends, week, every_nth_xTick, 
                               xlabel: str, ylabel: str, ylim, xTickLabels=None, legend=True):
    # Add the fill_between equivalent
    current_week_patch_trace = go.Scatter(
        x=[week_starts[week], week_ends[week], week_ends[week], week_starts[week]],
        y=[ylim[0], ylim[0], ylim[1], ylim[1]],
        fill='toself',
        fillcolor=myColor.mid_blue(0.4),
        line=dict(color=myColor.mid_blue(0.4)),
        name='Current week ice data',
        mode='none'
    )
    fig.add_trace(current_week_patch_trace, row=row, col=col)
    current_week_patch_trace_index = len(fig.data) - 1

    # Add the ULS draft signal plot
    uls_draft_trace = go.Scatter(
        x=time,
        y=draft,
        mode='lines',
        line=dict(color=myColor.dark_blue(1)),
        name='Raw ULS draft signal'
    )
    fig.add_trace(uls_draft_trace, row=row, col=col)
    uls_draft_trace_index = len(fig.data) - 1

    # Add the Ridge Peaks scatter plot
    keel_draft_flat = [x for xs in draft_ridge for x in xs]
    keel_dateNum_flat = [x for xs in time_ridge for x in xs]

    ridge_peaks_trace = go.Scatter(
        x=keel_dateNum_flat,
        y=keel_draft_flat,
        mode='markers',
        marker=dict(color=myColor.dark_red(1), size=3),
        name='Individual ridge peaks'
    )
    fig.add_trace(ridge_peaks_trace, row=row, col=col)
    ridge_peaks_trace_index = len(fig.data) - 1

    # Add the Level ice draft estimate step plot
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_draft_estimate_trace = go.Scatter(
        x=keel_dateNum_weekStart,
        y=draft_LI,
        mode='lines',
        line=dict(color=myColor.black(1)),
        name='Level ice draft estimate',
        line_shape='hv'
    )
    fig.add_trace(LI_draft_estimate_trace, row=row, col=col)
    LI_draft_estimate_trace_index = len(fig.data) - 1


    # Update x-axis ticks and labels
    dateNum_every_day = time[np.where(np.diff(time.astype(int)))[0] + 1]
    tickvals = dateNum_every_day[::every_nth_xTick]
    ticktext = xTickLabels[::every_nth_xTick] if xTickLabels is not None else None

    # Update layout
    fig.update_xaxes(
        title_text=xlabel,
        tickvals=tickvals,
        ticktext=ticktext,
        range=[time[0], time[-1]],
        automargin=True,
        row=row, col=col
    )
    fig.update_yaxes(
        title_text=ylabel, 
        range=[ylim[0], ylim[1]], 
        row=row, col=col)

    return fig, current_week_patch_trace_index, uls_draft_trace_index, ridge_peaks_trace_index, LI_draft_estimate_trace_index


def initialize_plot_weekly_data_draft(fig, row, col, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, week, 
                                      xlabel: str, ylabel: str, ylim, xTickLabels=None, dateTickDistance=1):

    # Convert time to np.array
    time = np.array(time)
    dateNum_every_day = time[week][np.where(np.diff(time[week].astype(int)))[0] + 1]

    # Add the Raw ULS draft signal line plot
    raw_uls_trace =go.Scatter(
        x=time[week],
        y=draft[week],
        mode='lines',
        line=dict(color=myColor.dark_blue(1)),
        name='Raw ULS draft signal'
    ) 
    fig.add_trace(raw_uls_trace, row=row, col=col)
    raw_uls_trace_index = len(fig.data) - 1

    # Add the Individual ridge peaks scatter plot
    ridge_peaks_trace = go.Scatter(
        x=time_ridge[week],
        y=draft_ridge[week],
        mode='markers',
        marker=dict(color=myColor.dark_red(1), size=3),
        name='Individual ridge peaks'
    )
    fig.add_trace(ridge_peaks_trace, row=row, col=col)
    ridge_peaks_trace_index = len(fig.data) - 1

    # Add the Level ice draft estimate step plot
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_draft_estimate_trace = go.Scatter(
        x=[keel_dateNum_weekStart[week], keel_dateNum_weekStart[week+1]],
        y=[draft_LI[week], draft_LI[week]],
        mode='lines',
        line=dict(color='green'),
        name='Level ice draft estimate',
        line_shape='hv'
    )
    fig.add_trace(LI_draft_estimate_trace, row=row, col=col)
    LI_draft_estimate_trace_index = len(fig.data) - 1

    # Update layout, ticks and labels
    tickvals = dateNum_every_day[:7:dateTickDistance]
    ticktext = xTickLabels[week*7:(week+1)*7:dateTickDistance] if xTickLabels is not None else None

    fig.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        row=row, col=col,
        automargin=True,
        range=[time[week][0], time[week][-1]],
        title_text=xlabel
    )
    fig.update_yaxes(title_text=ylabel, range=[ylim[0], ylim[1]], row=row, col=col)

    return fig, raw_uls_trace_index, ridge_peaks_trace_index, LI_draft_estimate_trace_index


def initialize_plot_spectrum(fig, row, col, HHi_plot, X_spectogram, Y_spectogram, time, draft, time_mean, LI_deepestMode, LI_deepestMode_expect, week_starts, week_ends, week, xlabel, ylabel, xTickLabels):

    # Add the color mesh (pcolormesh equivalent)
    heatmat_trace = go.Heatmap(
        z=HHi_plot.transpose(),
        y=Y_spectogram[:, 0], # first column of Y_spectogram (possible draft values) #draft,
        x=X_spectogram[0], # first row of X_spectogram (time values) #time_mean,
        colorscale='Viridis',
        showscale=True,
    )
    fig.add_trace(heatmat_trace, row=row, col=col)
    heatmat_trace_index = len(fig.data) - 1

    # Add the current week ice data patch
    current_week_patch_trace = go.Scatter(
        x=[week_starts[week], week_ends[week], week_ends[week], week_starts[week], week_starts[week]],
        y=[0, 0, max(draft), max(draft), 0],
        fill='toself',
        fillcolor=myColor.mid_blue(0.4),
        line=dict(color=myColor.mid_blue(0.4)),
        name='Current week ice data',
        mode='lines',
    )
    fig.add_trace(current_week_patch_trace, row=row, col=col)
    current_week_patch_trace_index = len(fig.data) - 1

    # Add the scatter plot for LI_deepestMode
    LI_deepestMode_trace = go.Scatter(
        x=time_mean,
        y=LI_deepestMode,
        mode='markers',
        marker=dict(color=myColor.dark_red(1), size=10, symbol='circle'),
        name='LI deepest mode',
    )
    fig.add_trace(LI_deepestMode_trace, row=row, col=col)
    LI_deepestMode_trace_index = len(fig.data) - 1

    # Add the scatter plot for LI_deepestMode_expect
    LI_deepestMode_expect_trace = go.Scatter(
        x=time_mean,
        y=LI_deepestMode_expect,
        mode='markers',
        marker=dict(color=myColor.dark_blue(1), size=10, symbol='triangle-up'),
        name='LI deepest mode expected',
    )
    fig.add_trace(LI_deepestMode_expect_trace, row=row, col=col)
    LI_deepestMode_expect_trace_index = len(fig.data) - 1

    # Add the rectangle patch for the current week
    lrs1x = (time_mean[-1] - time_mean[0]) / 20
    lrs1y = 4 / 20
    x_left = time_mean[week] - lrs1x / 2
    x_right = time_mean[week] + lrs1x / 2
    y_bottom = LI_deepestMode[week] - lrs1y / 2
    y_top = LI_deepestMode[week] + lrs1y / 2
    current_week_marker_trace = go.Scatter(
        x=[x_left, x_right, x_right, x_left, x_left],
        y=[y_bottom, y_bottom, y_top, y_top, y_bottom],
        fill='toself',
        fillcolor=myColor.black(0),
        line=dict(color=myColor.dark_red(1)),
        name='Current week marker',
        mode='lines',
    )
    fig.add_trace(current_week_marker_trace, row=row, col=col)
    current_week_marker_trace_index = len(fig.data) - 1
    # fig.add_shape(type='rect',
    #               x0=time_mean[week] - lrs1x / 2, y0=LI_deepestMode[week] - lrs1y / 2,
    #               x1=time_mean[week] + lrs1x / 2, y1=LI_deepestMode[week] + lrs1y / 2,
    #               line=dict(color=myColor.dark_red(1)),
    #               fillcolor=myColor.black(1),
    #               layer='above',
    #               )
    

     # Update layout
    time = np.array(time)
    dateNum_every_day = np.concatenate(time)[np.where(np.diff(np.concatenate(time).astype(int)))[0] + 1]
    dateTickDistance = 1
    every_nth_xTick = 50
    tickvals = dateNum_every_day[::every_nth_xTick]
    ticktext = xTickLabels[::every_nth_xTick] if xTickLabels is not None else None
    if len(ticktext) > len(tickvals):
        ticktext = ticktext[:-1]
    fig.update_xaxes(
        # tickvals=dateNum_every_day[:7:dateTickDistance],
        # ticktext=xTickLabels[week*7:(week+1)*7:dateTickDistance] if xTickLabels is not None else None,
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext,
        title_text=xlabel, 
        automargin=True,
        range=[np.concatenate(time)[0], np.concatenate(time)[-1]],
        # range=[time_mean[0]+3.5, time_mean[-1]-10.5], 
        row=row, col=col)
    fig.update_yaxes(title_text=ylabel, range=[0, 4], row=row, col=col)

    return fig, heatmat_trace_index, current_week_patch_trace_index, LI_deepestMode_trace_index, LI_deepestMode_expect_trace_index, current_week_marker_trace_index



def initialize_plot_weekly_data_scatter(fig, row, col, xData_all, yData_all, xData_thisYear, yData_thisYear, week, xlabel: str, ylabel: str):
    """Do the scatter plot of the weekly data using Plotly"""

    # Calculate rectangle dimensions
    lrs1x = (max(xData_all) - min(xData_all)) / 40
    lrs1y = (max(yData_all) - min(yData_all)) / 20

    # Add scatter plot for all data
    all_data_trace = go.Scatter(
        x=xData_all,
        y=yData_all,
        mode='markers',
        marker=dict(color=myColor.dark_blue(0.3), size=6, line=dict(color=myColor.dark_blue(0.6), width=1)), # opacity=0.5),
        name='all years/location',
    )
    fig.add_trace(all_data_trace, row=row, col=col)
    all_data_trace_index = len(fig.data) - 1

    # Add scatter plot for this year's data
    this_data_trace = go.Scatter(
        x=xData_thisYear,
        y=yData_thisYear,
        mode='markers',
        marker=dict(color=myColor.dark_red(1), size=4),
        name='this year/location',
    )
    fig.add_trace(this_data_trace, row=row, col=col)
    this_data_trace_index = len(fig.data) - 1

    # Add rectangle to mark the current data point (week)
    # Add the rectangle patch for the current week
    x_left = xData_thisYear[week] - lrs1x / 2
    x_right = xData_thisYear[week] + lrs1x / 2
    y_bottom = yData_thisYear[week] - lrs1y / 2
    y_top = yData_thisYear[week] + lrs1y / 2
    current_week_marker_trace = go.Scatter(
        x=[x_left, x_right, x_right, x_left, x_left],
        y=[y_bottom, y_bottom, y_top, y_top, y_bottom],
        fill='toself',
        fillcolor=myColor.black(0),
        line=dict(color=myColor.dark_red(1)),
        name='Current week marker',
        mode='lines',
    )
    fig.add_trace(current_week_marker_trace, row=row, col=col)
    current_week_marker_trace_index = len(fig.data) - 1
    # current_week_marker_trace_index = len(fig.data) - 1
    # fig.add_shape(type='rect',
    #               x0=xData_thisYear[week] - lrs1x / 2, y0=yData_thisYear[week] - lrs1y / 2,
    #               x1=xData_thisYear[week] + lrs1x / 2, y1=yData_thisYear[week] + lrs1y / 2,
    #               line=dict(color=myColor.black(1)),
    #               fillcolor=myColor.black(0),
    #               layer='above',
    #               row=row, col=col
    #               )
    
        # Update layout

    fig.update_xaxes(
        # tickvals=dateNum_every_day[:7:dateTickDistance],
        # ticktext=xTickLabels[week*7:(week+1)*7:dateTickDistance] if xTickLabels is not None else None,
        title_text=xlabel, 
        automargin=True,
        # range=[time_mean[0]+3.5, time_mean[-1]-10.5], 
        row=row, col=col)
    fig.update_yaxes(title_text=ylabel, row=row, col=col)

    return fig, all_data_trace_index, this_data_trace_index, current_week_marker_trace_index



def initialize_plot_kernelEstimation(fig, row, col, time, draft, week_starts, week_ends, week, LI_deepestMode_expect, LI_deepestMode, peaks_location, peaks_intensity, xlabel, ylabel):

    # Filter draft data for the current week
    draft_subset = draft[np.intersect1d(np.where(draft > 0), np.intersect1d(np.where(time > week_starts[week]), np.where(time < week_ends[week])))]

    # Kernel density estimate
    kde = scipy.stats.gaussian_kde(draft_subset)
    xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
    f = kde(xi)

        # Add the histogram
    number_of_bins = int((max(draft_subset) - min(draft_subset)) / 0.05)
    histogram_numpy = np.histogram(draft_subset, bins=number_of_bins, density=True)
    histogram_trace = go.Bar(
        x=histogram_numpy[1][:-1],
        y=histogram_numpy[0],
        marker=dict(color=myColor.black(0.7)),
        name='Histogram',
        width=(max(draft_subset) - min(draft_subset)) / number_of_bins,
    )
    fig.add_trace(histogram_trace, row=row, col=col)
    histogram_trace_index = len(fig.data) - 1

    # Add the deepest mode LI line
    LI_deepestMode_trace = go.Scatter(
        x=[LI_deepestMode_expect[week], LI_deepestMode_expect[week]],
        y=[0, 6],
        mode='lines',
        line=dict(color=myColor.dark_blue(1)),
        name='deepest mode LI',
    )
    fig.add_trace(LI_deepestMode_trace, row=row, col=col)
    LI_deepestMode_trace_index = len(fig.data) - 1

    # Add the average mode LI line
    LI_averageMode_trace = go.Scatter(
        x=[LI_deepestMode[week], LI_deepestMode[week]],
        y=[0, 6],
        mode='lines',
        line=dict(color=myColor.dark_red(1), dash='dash'),
        name='average mode LI',
    )
    fig.add_trace(LI_averageMode_trace, row=row, col=col)
    LI_averageMode_trace_index = len(fig.data) - 1

    # Add the kernel estimate line
    kernel_estimate_trace = go.Scatter(
        x=xi,
        y=f,
        mode='lines',
        line=dict(color=myColor.dark_red(1)),
        name='Kernel estimate',
    )
    fig.add_trace(kernel_estimate_trace, row=row, col=col)
    kernel_estimate_trace_index = len(fig.data) - 1

    # Add the peak signal scatter plot
    peak_signal_trace = go.Scatter(
        x=peaks_location[week],
        y=peaks_intensity[week],
        mode='markers',
        marker=dict(color=myColor.black(1), size=6),
        name='peak signal',
    )
    fig.add_trace(peak_signal_trace, row=row, col=col)
    peak_signal_trace_index = len(fig.data) - 1

    fig.update_xaxes(
        # tickvals=dateNum_every_day[:7:dateTickDistance],
        # ticktext=xTickLabels[week*7:(week+1)*7:dateTickDistance] if xTickLabels is not None else None,
        title_text=xlabel, 
        automargin=True,
        # range=[time_mean[0]+3.5, time_mean[-1]-10.5], 
        row=row, col=col)
    fig.update_yaxes(title_text=ylabel, row=row, col=col)

    return fig, histogram_trace_index, LI_deepestMode_trace_index, LI_averageMode_trace_index, kernel_estimate_trace_index, peak_signal_trace_index