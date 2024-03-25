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
rce = import_module('data_handling', 'ridge_compute_extract')
j2np = import_module('data_handling', 'json2numpy')

def ridge_statistics(poss_mooring_locs=['a', 'b', 'c', 'd'], years=list(range(2004, 2006+1))):
    """Do some statistics; need to be more description
    
    """
    # load the preprocessed data from the weekly_data.json file from the folder weekly_data in Data
    pathName = os.getcwd()
    path_to_json = os.path.join(pathName, 'Data', 'uls_data')

    # loop over mooring locations and years, if they are existing in the data, do calculations
    for year in years:
        for loc in poss_mooring_locs:
            sucess1, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}_{year+1}_{loc}_draft.json"), loc)
            sucess2, dateNum_rc, draft_rc, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}_{year+1}_ridge.json"), loc)
            sucess3, dateNum_LI, draft_LI, draft_mode = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}_{year+1}_LI.json"), loc)
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
            for week_num in range(len(dateNum_reshape)):
                dateNum_rc_reshape, draft_rc_reshape = rce.extract_weekly_data_draft_ridge(dateNum_rc, draft_rc, dateNum_reshape, draft_reshape,
                                        dateNum_rc_reshape, draft_rc_reshape, week_start, week_end, week_num)
                    
    # plot the data in different plots