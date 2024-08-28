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
    fig.data[trace_index].x = [week_starts[week], week_ends[week], week_ends[week], week_starts[week]]
    if ylim is not None:
        fig.data[trace_index].y = [ylim[0], ylim[0], ylim[1], ylim[1]]

    return fig