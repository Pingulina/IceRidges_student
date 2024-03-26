# parts of S003_ExtractWeeklyData.m are here

import numpy as np
import os
import sys
import json

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
rce = import_module('ridge_compute_extract', 'data_handling')
j2np = import_module('json2numpy', 'data_handling')

def ridge_statistics(poss_mooring_locs=['a', 'b', 'c', 'd'], years=list(range(2004, 2006+1))):
    """Do some statistics; need to be more description
    
    """
    # load the preprocessed data from the weekly_data.json file from the folder weekly_data in Data
    pathName = os.getcwd()
    path_to_json = os.path.join(pathName, 'Data', 'uls_data')

    # loop over mooring locations and years, if they are existing in the data, do calculations
    for year in years:
        for loc in poss_mooring_locs:
            sucess1, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)
            sucess2, dateNum_rc, draft_rc, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_ridge.json"), loc)
            sucess3, dateNum_LI, draft_LI, draft_mode = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_LI.json"), loc)
            if not (sucess1 and sucess2 and sucess3):
                print(f"Data for {loc} in {year} not found.")
                continue
            dateNum_reshape, draft_reshape = rce.extract_weekly_data_draft(dateNum, draft)
            # preallocate the variables
            week_start = np.zeros((len(dateNum_reshape)))
            week_end = np.zeros((len(dateNum_reshape)))
            # preallocate the dictionaries (store in dict, because the arrays for every week may be of different length, numpy doesn't like this)
            draft_rc_reshape = dict()
            dateNum_rc_reshape = dict()
            week_to_keep = np.zeros((len(dateNum_reshape)), dtype=bool)
            mean_keel_depth = np.zeros((len(dateNum_reshape)))
            dateNum_rc_pd = np.zeros((len(dateNum_reshape)))
            draft_max_weekly = np.zeros((len(dateNum_reshape)))


            for week_num in range(len(dateNum_reshape)):
                dateNum_rc_reshape, draft_rc_reshape, week_start, week_end = rce.extract_weekly_data_draft_ridge(dateNum_rc, draft_rc, dateNum_reshape, draft_reshape,
                                        dateNum_rc_reshape, draft_rc_reshape, week_start, week_end, week_num)
                
                # find a subset of the raw ULS draft measurement
                draft_subset = draft[np.intersect1d(
                    np.intersect1d(np.where(draft < 3), np.where(draft > 0)), 
                    np.intersect1d(np.where(dateNum > week_start[week_num]), np.where(dateNum < week_end[week_num]))
                    )]
                # if there are too few ridge data points, skip the week
                if len(dateNum_rc_reshape[week_num]) <= 5 or draft_subset.size == 0:
                    continue

                week_to_keep[week_num] = True

                # pd_ridges = exponential_fit() # fit exponential distribution to the ridges
                dateNum_rc_pd[week_num] = np.mean(dateNum_rc_reshape[week_num])
                mean_keel_depth[week_num] = np.mean(draft_reshape[week_num])
                draft_max_weekly[week_num] = np.max(draft_reshape[week_num]) # deepest weekly draft
                
            print(f"Data for {loc} in {year} extracted weekly.")
                    
    # plot the data in different plots