import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime as dt

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
    ### idea: plot function independent of the ridge_statistics function (load json file to get the data)
    # get the data from the json file (it contains a dict)
    dateNum = json_data[loc]['dateNum']
    draft = json_data[loc]['draft']
    dateNum_LI = json_data[loc]['dateNum_LI']
    draft_mode = json_data[loc]['draft_mode']
    dateNum_rc = json_data[loc]['dateNum_rc']
    draft_rc = json_data[loc]['draft_rc']
    dateNum_rc_pd = json_data[loc]['dateNum_rc_pd']
    draft_deepest_ridge = json_data[loc]['draft_deepest_ridge']
    deepest_mode_weekly = json_data[loc]['deepest_mode_weekly']
    week_to_keep = json_data[loc]['week_to_keep']
    number_ridges = json_data[loc]['number_ridges']


    # Create a subplot figure with 2 rows and 2 columns
    fig = make_subplots(rows=2, cols=2, subplot_titles=('Weekly Ice Thickness', 'Weekly Number of Ridges'))

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

    fig.update_layout(height=600, width=1200, title_text='Ridge Statistics')

    return fig