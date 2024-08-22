import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime as dt
import os
import sys

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
j2d = import_module('jsonified2dict', 'data_handling')

def plot_per_location(json_data, year=2004, loc='a'):
    """
    :param dateNum: numpy array, dates
    :param draft: numpy array, draft data
    :param dateNum_LI: numpy array, level ice dates
    :param draft_mode: numpy array, level ice draft data
    :param dateNum_rc: numpy array, ridge dates
    :param draft_rc: numpy array, ridge draft data
    :param dateNum_rc_pd: numpy array, ridge dates (processed)
    :param draft_deepest_ridge: numpy array, deepest ridge draft data
    :param deepest_mode_weekly: numpy array, weekly deepest mode data
    :param week_to_keep: numpy array, week to keep
    :param R_no: numpy array, number of ridges
    :return: fig: plotly figure, figure with the ridge statistics
    """
    print('plot_per_location plotly')
    ### idea: plot function independent of the ridge_statistics function (load json file to get the data)
    # get the data from the json file (it contains a dict)
    json_data = j2d.jsonified2dict(json_data[loc]) # this is to convert the jsonified data to a dict with its original data types
    dateNum_LI = np.array(json_data['dateNum_LI'])
    draft_mode = np.array(json_data['draft_mode'])
    dateNum_rc = np.array(json_data['dateNum_rc'])
    draft_rc = np.array(json_data['draft_rc'])
    dateNum_rc_pd = np.array(json_data['mean_dateNum'])
    draft_deepest_ridge = np.array(json_data['expect_deepest_ridge'])
    deepest_mode_weekly = np.array(json_data['level_ice_deepest_mode'])
    week_to_keep = np.array(json_data['week_to_keep']) #, dtype=int) # must be int
    number_ridges = np.array(json_data['number_ridges'])
    mean_keel_draft = np.array(json_data['mean_keel_draft'])
    draft_max_weekly = np.array('draft_weekly_deepest_ridge')

    dateNum = np.array(json_data['dateNum'])
    draft = np.array(json_data['draft'])


    # Create a subplot figure with 2 rows and 2 columns
    fig = make_subplots(
        rows=2, cols=3, 
        subplot_titles=(
            'weekly ice thickness', 'weekly number of ridges',
            'deepest weekly ridge', 'number of ridges',
            'accuracy of prediction'
        )
    )

    # Weekly ice thickness plot
    newDayIndex = np.where(dateNum.astype(int) - np.roll(dateNum.astype(int), 1) != 0)
    dateTicks = [str(dt.fromordinal(thisDate))[0:7] for thisDate in dateNum[newDayIndex[0][::60]].astype(int)]

    fig.add_trace(go.Scatter(x=dateNum, y=draft, mode='lines', line=dict(width=0.1, color='blue'), name='Draft'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dateNum_LI, y=draft_mode, mode='lines', line=dict(width=0.6, color='red'), name='Level Ice Draft'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dateNum_rc, y=draft_rc, mode='markers', marker=dict(size=2, color='red'), name='Ridge Draft'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dateNum_rc_pd[week_to_keep], y=draft_deepest_ridge[week_to_keep], mode='lines', line=dict(color='black'), name='Draft Weekly Deepest Ridge'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dateNum_rc_pd[week_to_keep], y=deepest_mode_weekly[week_to_keep], mode='lines', line=dict(color='black', dash='dash'), name='Level Ice Weekly Deepest Mode'), row=1, col=1)

    fig.update_xaxes(title_text='Date', tickvals=dateNum[newDayIndex[0][::60]], ticktext=dateTicks, row=1, col=1)
    fig.update_yaxes(title_text='Draft [m]', row=1, col=1)

    # Weekly number of ridges plot
    fig.add_trace(go.Scatter(x=dateNum_rc_pd[week_to_keep], y=number_ridges[week_to_keep], mode='lines', line=dict(color='black'), name='Number of Ridges'), row=1, col=2)

    fig.update_xaxes(title_text='Date', tickvals=dateNum[newDayIndex[0][::60]], ticktext=dateTicks, row=1, col=2)
    fig.update_yaxes(title_text='Number of Ridges', range=[0, 400], row=1, col=2)

    
    # deepest weekly ridge
    fig.add_trace(go.Scatter(x=deepest_mode_weekly, y=draft_deepest_ridge, mode='markers', marker=dict(size=2, color='red'), name='expected deepest weekly ridge'), row=1, col=3)
    fig.add_trace(go.Scatter(x=deepest_mode_weekly, y=mean_keel_draft+5, mode='markers', marker=dict(size=2, color='blue'), name='expected mean weekly keel depth'), row=1, col=3)
    fig.add_trace(go.Scatter(x=deepest_mode_weekly, y=draft_max_weekly, mode='markers', marker=dict(size=2, color='green'), name='weekly deepest ridge'), row=1, col=3)
    fig.update_xaxes(title_text="Level ice thickness [m]", row=1, col=3, range=[0, 3])
    fig.update_yaxes(title_text="Ridge thickness [m]", row=1, col=3, range=[0, 30])

    # number of ridges over mean keel depth
    fig.add_trace(go.Scatter(x=mean_keel_draft+5, y=number_ridges, mode='markers', marker=dict(size=2, color='blue'), name='Mean keel depth'), row=2, col=1)
    fig.add_trace(go.Scatter(x=deepest_mode_weekly, y=number_ridges, mode='markers', marker=dict(size=2, color='red'), name='deepest mode level ice'), row=2, col=1)
    fig.update_xaxes(title_text="Draft [m]", row=2, col=1, range=[0, 10])
    fig.update_yaxes(title_text="Number of ridges", row=2, col=1)

    # expected deepest keel vs measured deepest keel
    fig.add_trace(go.Scatter(x=np.arange(0, 30, 1), y=np.arange(0, 30, 1), mode='lines', line=dict(color='black', width=0.5), name='Expected vs Measured'), row=2, col=2)
    fig.add_trace(go.Scatter(x=deepest_mode_weekly, y=draft_max_weekly, mode='markers', marker=dict(size=2, color='green'), name='Measured deepest keel'), row=2, col=2)
    fig.update_xaxes(title_text="Expected deepest keel [m]", row=2, col=2, range=[0, 30])
    fig.update_yaxes(title_text="Measured deepest keel [m]", row=2, col=2, range=[0, 30])

    fig.update_layout(height=900, width=1200, title_text='Ridge Statistics')

    return fig