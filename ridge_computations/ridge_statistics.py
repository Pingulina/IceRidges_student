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
# rc = import_module('rayleigh_criterion', 'helper_functions')

def ridge_statistics(poss_mooring_locs=['a', 'b', 'c', 'd'], years=list(range(2004, 2006+1))):
    """Do some statistics; need to be more description
    
    """
    # load the preprocessed data from the weekly_data.json file from the folder weekly_data in Data
    pathName = os.getcwd()
    data = json.load(open(os.path.join(pathName, 'Data', 'weekly_data', f"mooring_{years[0]}-{years[-1]}.json")))
    # the format of data is a dictionary with {"{loc}_{yr}": {"dateNum": [], "draft": [], "datNum_rc": [], "draft_rc": [], "dateNum_LI": [], "draft:LI": []}, ...}
    # all data are in weekly format (7 days per column)

    # loop over mooring locations and years, if they are existing in the data, do calculations
    for loc in poss_mooring_locs:
        for yr in years:
            key = f"{loc}_{yr}"
            if key in data:
                print(f"Calculating statistics for {key}")
                # extract the data
                dateNum_reshape = np.array(data[key]['date_num_reshape'])
                dateNum_reshape_rc = np.array(data[key]['date_num_reshape_rc'])
                draft_reshape = np.array(data[key]['draft_reshape'])
                draft_reshape_rc = np.array(data[key]['draft_reshape_rc'])
                dateNum_LI = np.array(data[key]['date_num_LI'])
                draft_LI = np.array(data[key]['draft_LI'])
                draft_mode = np.array(data[key]['draft_mode'])

                # load the ridge-separated data for this location and year from rc_{loc}_{yr}-{yr+1}_draft.json from the folder RC_data in Data
                data_rc = json.load(open(os.path.join(pathName, 'Data', 'RC_data', f"rc_{loc}_{yr}-{yr+1}_draft.json")))
                dateNum_rc = np.array(data_rc['dateNum'])
                draft_rc = np.array(data_rc['draft'])
                # do some calculations
                # loop through the weeks (this needs to be improved, perhaps matrix calculations are possible
                for i in range(dateNum_reshape.shape[1]):
                    dateNum_rc_reshape = dateNum_rc[np.where(dateNum_rc > dateNum_reshape_rc[0, i] and dateNum_rc < dateNum_reshape_rc[-1, i])]
                    draft_rc_reshape = draft_rc[np.where(dateNum_rc > dateNum_reshape_rc[0, i] and dateNum_rc < dateNum_reshape_rc[-1, i])]
                # deepest weekly ridge

                # bandwidth parameter of the kernel estimate of the draft PDF

                # kernel estimate of the draft PDF

                # estimating the expected deepest ridge
            else:
                pass
    
    # plot the data in different plots