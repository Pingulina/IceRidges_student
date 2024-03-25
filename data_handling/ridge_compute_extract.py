# this moduel contains functions for the ridge statistics

import os
import numpy as np

import os
import sys

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
# Get the current working directory
cwd = os.getcwd()
# Construct the path to the base directory
base_dir = os.path.join(cwd, '..')
# Add the base directory to sys.path
sys.path.insert(0, base_dir)
from import_module import import_module
constants = import_module('constants', 'helper_functions')

# extraction of the weekly data (reshaping the data in a weekly format)
def extract_weekly_data_draft(dateNum:np.ndarray, draft:np.ndarray):
    """Extract the weekly data from the input data
    :param dateNum: np.array, date number of the data
    :param draft: np.array, draft of the data
    :return: np.array, np.array, reshaped date number and draft data
    """

    # Ridge statistics
    # transferring the time vector in a matrix dateTime_reshape_rc with N columns (weeks)
    # mean time interval between two measurements
    dt_days = np.mean(np.diff(dateNum))
    dt = np.round(dt_days * constants.hours_day * constants.seconds_hour)
    mean_dateNum_rc = 3600 * 24 * constants.level_ice_statistics_days # seconds per level_ice_statistics_days unit (meaning 7 days in seconds)
    mean_points_rc = mean_dateNum_rc / dt # data points per level_ice_statistics_days unit
    no_e_rc = int(np.floor(len(dateNum)/mean_points_rc) * mean_points_rc) # number of elements to take in, so ti is dividable with number of 'mean_points' per specified 'lecel_ice_time'
    dateNum_reshape = dateNum[:no_e_rc] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
    dateNum_reshape = dateNum_reshape.reshape(int(mean_points_rc), int(len(dateNum)/mean_points_rc))
    draft_reshape = draft[:no_e_rc]
    draft_reshape = draft_reshape.reshape(int(mean_points_rc), int(len(draft)/mean_points_rc))

    return dateNum_reshape, draft_reshape


def extract_weekly_data_draft_ridge(dateNum_rc:np.ndarray, draft_rc:np.ndarray, dateNum_reshape:np.ndarray, draft_reshape:np.ndarray,
                                    dateNum_rc_reshape:dict, draft_rc_reshape:dict, week_start:np.ndarray, week_end:np.ndarray, 
                                    week_num:int):
    """Extract the weekly data from the input data
    :param dateNum_rc: np.array, date number of the data
    :param draft_rc: np.array, draft of the data
    :return: np.array, np.array, reshaped date number and draft data
    """
    week_start[week_num] = dateNum_reshape[0, week_num]
    week_end[week_num] = dateNum_reshape[-1, week_num]
    week_start_idx = np.where(dateNum_rc == week_start)
    week_end_idx = np.where(dateNum_rc == week_end)
    dateNum_rc_reshape[week_num] = dateNum_reshape[week_start_idx:week_end_idx]
    draft_rc_reshape[week_num] = draft_reshape[week_start_idx:week_end_idx]

    return dateNum_rc_reshape, draft_rc_reshape, week_start, week_end
