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


    # update week patch in draft overview plot
    fig = data_analysis_plot_plotly_update.update_current_week_patch(fig, dict_trace_indices['draftAll_patch_trace_index'], week_starts, week_ends, week)

    return fig