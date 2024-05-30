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
    mean_dateNum_rc = 3600 * 24 * constants.level_ice_statistic_days # seconds per level_ice_statistics_days unit (meaning 7 days in seconds)
    mean_points_rc = mean_dateNum_rc / dt # data points per level_ice_statistics_days unit
    no_e_rc = int(np.floor(len(dateNum)/mean_points_rc) * mean_points_rc) # number of elements to take in, so ti is dividable with number of 'mean_points' per specified 'lecel_ice_time'
    dateNum_reshape = dateNum[:no_e_rc] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
    dateNum_reshape = dateNum_reshape.reshape(int(len(dateNum)/mean_points_rc), int(mean_points_rc))
    draft_reshape = draft[:no_e_rc]
    draft_reshape = draft_reshape.reshape(int(len(draft)/mean_points_rc), int(mean_points_rc))

    return dateNum_reshape, draft_reshape

def extract_hourly_data_draft(dateNum:np.ndarray, draft:np.ndarray):
    """Extract the hourly data from the input data
    :param dateNum: np.array, date number of the data
    :param draft: np.array, draft of the data
    :return: np.array, np.array, reshaped date number and draft data
    """

    # Ridge statistics
    # transferring the time vector in a matrix dateTime_reshape_rc with N columns (weeks)
    # mean time interval between two measurements
    dt_days = np.mean(np.diff(dateNum)) # time difference in days
    dt = np.round(dt_days * constants.hours_day * constants.seconds_hour) # convert the time difference to seconds
    mean_dateNum_rc = 3600  # seconds per hour unit 
    mean_points_rc = mean_dateNum_rc / dt # data points per level_ice_statistics_days unit
    no_e_rc = int(np.floor(len(dateNum)/mean_points_rc) * mean_points_rc) # number of elements to take in, so ti is dividable with number of 'mean_points' per specified 'lecel_ice_time'
    dateNum_reshape = dateNum[:no_e_rc] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
    dateNum_reshape = dateNum_reshape.reshape(int(len(dateNum)/mean_points_rc), int(mean_points_rc))
    draft_reshape = draft[:no_e_rc]
    draft_reshape = draft_reshape.reshape(int(len(draft)/mean_points_rc), int(mean_points_rc))

    return dateNum_reshape, draft_reshape


def extract_weekly_data_draft_ridge(dateNum_rc:np.ndarray, draft_rc:np.ndarray, dateNum_reshape:np.ndarray, draft_reshape:np.ndarray,
                                    dateNum_rc_reshape:dict, draft_rc_reshape:dict, week_start:np.ndarray, week_end:np.ndarray, 
                                    week_num:int):
    """Extract the weekly data from the input data
    :param dateNum_rc: np.array, date number of the data
    :param draft_rc: np.array, draft of the data
    :param dateNum_reshape: np.array, reshaped date number of the data (weekly data)
    :param draft_reshape: np.array, reshaped draft of the data (weekly data)
    :param dateNum_rc_reshape: np.array, reshaped date number of the ridge data (weekly data)
    :param draft_rc_reshape: np.array, reshaped draft of the ridge data (weekly data)
    :param week_start: np.array, int, start of the week
    :param week_end: np.array, int, end of the week
    :param week_num: int, number of the week
    :return: np.array, np.array, reshaped date number and draft data
    """
    week_start[week_num] = dateNum_reshape[week_num][0]
    week_end[week_num] = dateNum_reshape[week_num][-1]
    week_start_idx, week_end_idx = find_dateTime_in_week(dateNum_rc, week_start[week_num], week_end[week_num])
    dateNum_rc_reshape[week_num] = dateNum_rc[week_start_idx:week_end_idx]
    draft_rc_reshape[week_num] = draft_rc[week_start_idx:week_end_idx]

    return dateNum_rc_reshape, draft_rc_reshape, week_start, week_end


def find_dateTime_in_week(dateNum, week_start, week_end):
    """Find the indices of dateNum, that describes the first and last element inbetween week_start and week_end
    :param dateNum: np.array, date number of the data
    :param week_start: float, dateNum of the start of the week
    :param week_end: float, dateNum of the end of the week
    return: int, int, indices of the first and last element in the week
    """
    week_start_idx = np.where(dateNum >= week_start)[0][0] # find the first element, that is larger or equal to week_start
    week_end_idx = np.where(dateNum <= week_end)[0][-1]+1 # find the last element, that is smaller or equal to week_en
    if np.isnan(week_start_idx) or np.isnan(week_end_idx):
        # return 0, 0, such that no data is written to the dateNum_reshape (since there is no needed data in this week)
        week_start_idx = 0
        week_end_idx = 0
    if week_end_idx == len(dateNum):
        week_end_idx = np.nan # if the end of the week is the last element in the data, return nan, such that the last element is also included
    return week_start_idx, week_end_idx
