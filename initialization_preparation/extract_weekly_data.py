# parts of S003_ExtractWeeklyData.m are in this file
import numpy as np
import json
import scipy.stats
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
### imports using the helper function import_module
# import the date_time_stuff module from the helper_functions directory
rc = import_module('rayleigh_criterion', 'helper_functions')


def extract_weekly_data(estimate_hourly=True):
    """sort the data from the json file into weekly data and store it back to json file
    :return: None
    """

    # choose, which locations from which years should be processed 
    # TODO: choosing locations and years should be done via the GUI (table with tickboxes)
    mooring_locations = ['a', 'b', 'c', 'd']
    level_ice_time = 1 # duration of sample for level ice estimate (in hours)
    level_ice_statistics_days = 7 # duration of sample of estimated level ice for level ice statistics (in days)

    yrs_loc_dict = {} # dictionary with years as keys and the locations as values - only used for creation of the loc_yrs_dict
    loc_yrs_dict = {} # dicitonary with the locations as keys and the years as values

    # years to be processed
    years = [2004, 2005, 2006]
    for year in years:
        yrs_loc_dict[year] = mooring_locations

    print(f"For the years {years}, the following locations will be processed by default: {mooring_locations}")
    change_default_locations = input("Do you want to change the default locations? - Y/y, N/n:")
    if change_default_locations == 'Y' or change_default_locations == 'y':
        for year,mooring in yrs_loc_dict.items():
            change_mooring_locations = input(f"Would you like to change the locations for the year {year}? - Y/y, N/n:")
            if change_mooring_locations == 'Y' or change_mooring_locations == 'y':
                yrs_loc_dict[year] = input(f"Enter the locations to be processed for the year {year} (separated by a comma): ").split(',')
                print(f"For the year {year}, the following locations will be processed: {yrs_loc_dict[year]}")

    # transpose the dictionary, so that the locations are the keys and the years are the values
    for year, locs in yrs_loc_dict.items():
        for loc in locs:
            if loc in loc_yrs_dict:
                loc_yrs_dict[loc].append(year)
            else:
                loc_yrs_dict[loc] = [year]
    
    dict_weekly_data = {} # dictionary to store the weekly data
    # iterate over the mooring locations
    for loc_mooring, yrs in loc_yrs_dict.items():
        for yr in yrs:
            print(f"Processing the location {loc_mooring} for the season {yr}-{yr+1}")
            # load the data from the json file for location loc_mooring and year yr
            # the file is located in the folder mooring_data in the Data folder
            # the file name is ulsYYx_draft.json, where YY is the last two digits of the year and x is the location
            # the file is within the folder YYYY-YYYY+1

            # read the json file
            with open(f"Data/mooring_data/{yr}-{yr+1}/uls{str(yr)[2:]}{loc_mooring}_draft.json") as json_file:
                data = json.load(json_file)

            draft = np.array(data['draft'])
            dateNum = np.array(data['dateNum'])

            # mean time interval between two measurements
            dt_days = np.mean(np.diff(dateNum)) # time step in dateNum format (days)            
            # if there is a missmatch in the data time, fix it
            if not min(np.diff(dateNum)) == dt_days:
                print("There is a missmatch in the time data. Fixing it automatically.")
                dateNum = np.arange(dateNum[0], dateNum[-1], dt_days)
            # transform dt_days in seconds
            hours_day = 24
            seconds_hour = 3600
            dt = dt_days * hours_day * seconds_hour

            # if the data is not measured hourly, estimate the hourly data, if estimate_hourly is True
            if estimate_hourly:
                # reshaping the time and draft matrices to calcualte means and modes
                mean_time = 3600 * level_ice_time # time in seconds, where the ice is considered to be level
                mean_points = int(mean_time / dt) # number of points in the mean_time interval
                # number of elements to take in, so ti is dicidable with number of 'mean_points' per specified 'lecel_ice_time'
                no_e = int(np.floor(len(dateNum)/mean_points)) * mean_points

                dateNum_reshape = dateNum[:no_e] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
                dateNum_reshape = dateNum_reshape.reshape(int(mean_points), int(len(dateNum_reshape)/mean_points))
                draft_reshape = draft[:no_e]
                draft_reshape = draft_reshape.reshape(int(mean_points), int(len(draft_reshape)/mean_points))

                # estimating the level ice draft
                draft_LI = np.mean(draft_reshape, axis=0)
                draft_mode = np.zeros(len(draft_LI))
                # making a karnel PDF from the data
                for column, i in enumerate(draft_reshape):
                    kde = scipy.stats.gaussian_kde(column)
                    x = np.linspace(min(column), max(column), 1000)
                    p = kde(x)
                    pmax = max(p)
                    imax = np.argmax(p)
                    draft_mode[i] = x[imax]

            # rayleigh criterion
            
            
            # store the data in a json file
            storage_name = f"rc_{loc_mooring}_{yr}-{yr+1}.json"
            # if the folder RC_data does not exist, create it
            storage_path = os.path.join('Data', 'RC_data')            
            file_storage = os.path.join(storage_path, storage_name)
            # if file_storage esists, load it. Else compute rayleigh criterion and store it
            if os.path.exists(file_storage):
                with open(file_storage, 'r') as file:
                    rc_data = json.load(file)
                dateNum_rc = np.array(rc_data['dateNum'])
                draft_rc = np.array(rc_data['draft'])
            else:
                dateNum_rc, draft_rc = rc.rayleigh_criterion(dateNum, draft, threshold_draft=2.5, min_draft=5.0)
                if not os.path.exists(storage_path):
                    os.makedirs(storage_path)
                with open(file_storage, 'w') as file:
                    json.dump({'dateNum': dateNum_rc, 'draft': draft_rc}, file)
            

            # Ridge statistics
            # transferring the time vector in a matrix dateTime_reshape_rc with N columns (weeks)
            mean_dateNum_rc = 3600 * 24 * level_ice_statistics_days
            mean_points_rc = mean_dateNum_rc / dt
            no_e_rc = np.floor(len(dateNum_rc)/mean_points_rc) * mean_points_rc # number of elements to take in, so ti is dicidable with number of 'mean_points' per specified 'lecel_ice_time'
            dateNum_reshape_rc = dateNum_rc[:no_e_rc] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
            dateNum_reshape_rc = dateNum_reshape_rc.reshape(int(mean_points_rc), int(len(dateNum_reshape_rc)/mean_points_rc))
            draft_reshape_rc = draft_rc[:no_e_rc]
            draft_reshape_rc = draft_reshape_rc.reshape(int(mean_points_rc), int(len(draft_reshape_rc)/mean_points_rc))

            # store dateNum_reshape_rc in dict_weekly_data with key loc_mooring and yr
            dict_weekly_data[f"{loc_mooring}_{yr}"] = {'date_num_reshape': dateNum_reshape, 'date_num_reshape_rc': dateNum_reshape_rc, 'draft_reshape': draft_reshape, 'draft_reshape_rc': draft_reshape_rc}


    # store the weekly data in a json file
    storage_name = 'weekly_data.json'
    storage_path = os.path.join('Data', 'RC_data')
    file_storage = os.path.join(storage_path, storage_name)
    # if the storage path does not exist, create it
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    with open(file_storage, 'w') as file:
        json.dump(dict_weekly_data, file)

    print(f"Weekly data stored in {file_storage}")
            