import plotly.graph_objects as go
import numpy as np
import os
import sys
import scipy.stats

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants = import_module('constants', 'helper_functions')
data_analysis_plot_plotly_update = import_module('data_analysis_plot_plotly_update', 'plot_functions')
j2d = import_module('jsonified2dict', 'data_handling')
date_time_stuff = import_module('date_time_stuff', 'helper_functions')

def weekly_analysis_update_plot(year, loc, week, fig, dict_ridge_statistics_allYears, dict_ridge_statistics_jsonified, dict_trace_indices):
    ### get the variables out of the dicts
    all_LIDM = dict_ridge_statistics_allYears['all_LIDM']
    all_MKD = dict_ridge_statistics_allYears['all_MKD']
    all_Dmax = dict_ridge_statistics_allYears['all_Dmax']
    all_number_of_ridges = dict_ridge_statistics_allYears['all_number_of_ridges']

    if year in dict_ridge_statistics_jsonified.keys():
        dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified[str(year)][loc]) # this is to convert the jsonified data to a dict with its original data types
    else:
        dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified[loc])
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


    every_nth = 50
    dateNum_every_day = dateNum[np.where(np.diff(dateNum.astype(int)))[0]+1]
    xTickLabels = date_time_stuff.datestr(dateNum_every_day, format='DD.MM.YY')

    if week > len(dateNum_reshape)-1:
        return fig, True, f"Week index out of range. The maximum week for this location is {len(dateNum_reshape)}."

    # update week patch in draft overview plot
    fig = data_analysis_plot_plotly_update.update_current_week_patch(fig, dict_trace_indices['draftAll_patch_trace_index'], week_starts, week_ends, week)

    # update the weekly draft plot
    fig = data_analysis_plot_plotly_update.update_plot_weekly_data_draft(
        fig=fig, draftThis_trace_index=dict_trace_indices['draftThis_trace_index'], draftThis_peaks_trace_index=dict_trace_indices['draftThis_peaks_trace_index'], 
        draftThis_LIdraft_e_trace_index=dict_trace_indices['draftThis_LIdraft_e_trace_index'], time=dateNum_reshape, draft=draft_reshape, 
        time_ridge=dateNum_ridge, draft_ridge=draft_ridge, time_LI=dateNum_reshape, draft_LI=deepest_mode_weekly, week=week, 
        xTickLabels=xTickLabels, dateTickDistance=2
    )
    
    # update the weekly spectrum plot
    fig = data_analysis_plot_plotly_update.update_plot_spectrum(
        fig=fig, heatmap_patch_trace_index=dict_trace_indices['heatmap_patch_trace_index'], heatmap_marker_trace_index=dict_trace_indices['heatmap_marker_trace_index'], 
        time_mean=dateNum_rc_pd, LI_deepestMode=deepest_mode_weekly, week_starts=week_starts, week_ends=week_ends, week=week
    )
    
    ### update the scatter plots

    # Mean Ridge Keel Depth
    fig = data_analysis_plot_plotly_update.update_plot_weekly_data_scatter_marker(
        fig=fig, current_week_marker_trace_index=dict_trace_indices['meanKeelDraft_marker_trace_index'], xData_all=all_LIDM, yData_all=all_MKD, 
        xData_thisYear=deepest_mode_weekly, yData_thisYear=mean_keel_draft, week=week
    )


    # Weekly Deepest Ridge
    fig = data_analysis_plot_plotly_update.update_plot_weekly_data_scatter_marker(
        fig=fig, current_week_marker_trace_index=dict_trace_indices['maxKeelDraft_marker_trace_index'], xData_all=all_LIDM, yData_all=all_Dmax, 
        xData_thisYear=deepest_mode_weekly, yData_thisYear=draft_max_weekly, week=week
    )
    
    # Number of Ridges
    fig = data_analysis_plot_plotly_update.update_plot_weekly_data_scatter_marker(
        fig=fig, current_week_marker_trace_index=dict_trace_indices['numRidges_marker_trace_index'], xData_all=all_LIDM, yData_all=all_number_of_ridges, 
        xData_thisYear=deepest_mode_weekly, yData_thisYear=number_ridges, week=week
    )

    return fig, False, ''