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
mooring_locs = import_module('mooring_locations', 'helper_functions')
d2d = import_module('data2dict', 'initialization_preparation')
constants = import_module('constants', 'helper_functions')


def extract_ridge_LI_data(estimate_hourly=True, overwrite=False, sample_rate = 0.5):
    """sort the data from the json file into weekly data and store it back to json file
    :param estimate_hourly: bool, optional, if True, the hourly data is estimated from the available data
    :param years: list, optional, list of years to be processed
    :param mooring_locations: list, optional, list of mooring locations to be processed
    :param overwrite: bool, optional, if True, the existing files are overwritten, if False, the existing files are skipped
    :param sample_rate: float, optional, sample rate of the data in Hz
    :return: None
    """
    
    dict_mooring_locations = mooring_locs.mooring_locations(storage_path='Data') # dictionary with the mooring locations
    
    # choose, which locations from which years should be processed 
    # TODO: choosing locations and years should be done via the GUI (table with tickboxes)
    print(f"Data from the following seasons was found and will be processed by default: {dict_mooring_locations.keys()}")
    change_default_seasons = input("Do you want to change the default seasons? - Y/y, N/n:")
    if change_default_seasons == 'Y' or change_default_seasons == 'y':
        change_seasons = input("Enter the seasons to be processed (separated by a comma), format: start_year-end_year: ").split(',')
        for season in change_seasons:
            if season not in dict_mooring_locations:
                print(f"Season {season} not found in the data.")
                change_seasons.remove(season)
                if len(change_seasons)==0:
                    print("No season to evaluate. This need to be catched!!!")

            print(f"For the season {season}, the following locations will be processed by default: {dict_mooring_locations[season].keys()}")
            change_default_locations = input("Do you want to change the default locations? - Y/y, N/n:")
            if change_default_locations == 'Y' or change_default_locations == 'y':
                new_locations = input(f"Enter the locations to be processed for the season {season} (separated by a comma): ").split(',')
                for loc in new_locations:
                    if loc not in dict_mooring_locations[season]:
                        print(f"Location {loc} not found in the data.")
                        new_locations.remove(loc)
                # remove all locations from the season, that are not in new_locations
                dict_mooring_locations[season] = {loc: dict_mooring_locations[season][loc] for loc in new_locations}
            # remove all seasons from the dict, that are not in change_seasons
        dict_mooring_locations = {season: dict_mooring_locations[season] for season in change_seasons}
        newLine = '\n'
        print(f"The following seasons will be processed: \n{newLine.join([f'{year}: {list(dict_mooring_locations[year].keys())}' for year in dict_mooring_locations.keys()])}")
    storage_path = os.path.join(os.getcwd(), 'Data', 'uls_data')
    for mooring_period in dict_mooring_locations:
        yr = int(mooring_period.split('-')[0])

        # if the storage path does not exist, create it
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        # the data should be stored as json files
        dict_draft = {}
        # if there is already a json file for ridge and level ice, load it; else initialize an empty dict
        try:
            with open(os.path.join(storage_path, f"mooring_{yr}-{yr+1}_ridge.json"), 'r') as file:
                dict_draft_ridge = json.load(file)
        except FileNotFoundError:
            dict_draft_ridge = {}
        try:
            with open(os.path.join(storage_path, f"mooring_{yr}-{yr+1}_LI.json"), 'r') as file:
                dict_draft_LI = json.load(file)
        except FileNotFoundError:
            dict_draft_LI = {}
        

        for loc_mooring in dict_mooring_locations[mooring_period]:
            print(f"Processing the location {loc_mooring} for the season {yr}-{yr+1}")
            # reset the draft dict (every location is stored in a separate dict and json file)
            dict_draft = {}

            # load the data from the dat file and store it in a dict
            # data_dict = d2d.data2dict(os.path.join(os.getcwd(), 'Data_Beaufort_Gyre_Exploration', mooring_period), f"uls{mooring_period[2:4]}{loc_mooring}_draft.dat")
            data_dict = d2d.json2dict(os.path.join(os.getcwd(), 'Data', 'mooring_data', mooring_period), f"uls{mooring_period[2:4]}{loc_mooring}_draft.json")
            # remove date and time from the dict
            data_dict.pop('date')
            data_dict.pop('time')
            # meaning only keep position_info, dateNum and draft
            dateNum = np.array(data_dict['dateNum'])
            draft = np.array(data_dict['draft'])
            # fit dateNum to sample rate (full seconds)
            dateNum = np.round(dateNum * 1/sample_rate * (3600 * 24)) / (1/sample_rate * (3600 * 24))


            # mean time interval between two measurements
            dt_days = np.mean(np.diff(dateNum)) # time step in dateNum format (days)            
            # if there is a missmatch in the data time, fix it
            if not np.isclose(min(np.diff(dateNum)), dt_days, atol=1e-8):
                print("There is a missmatch in the time data. Fixing it automatically.")
                dateNum = np.arange(dateNum[0], dateNum[-1], dt_days)
            # transform dt_days in seconds
            dt = np.round(dt_days * constants.hours_day * constants.seconds_hour) # FIXME: this is a restriction that only natural numbers are allowed for dt

            # if the data is not measured hourly, estimate the hourly data, if estimate_hourly is True
            if estimate_hourly:
                # reshaping the time and draft matrices to calcualte means and modes
                mean_time = 3600 * constants.level_ice_time # time in seconds, where the ice is considered to be level
                mean_points = int(mean_time / dt) # number of points in the mean_time interval
                # number of elements to take in, so ti is dicidable with number of 'mean_points' per specified 'lecel_ice_time'
                no_e = int(np.floor(len(dateNum)/mean_points)) * mean_points

                dateNum_reshape = dateNum[:no_e] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
                dateNum_reshape = dateNum_reshape.reshape(int(len(dateNum_reshape)/mean_points), int(mean_points))
                draft_reshape = draft[:no_e]
                draft_reshape = draft_reshape.reshape(int(len(draft_reshape)/mean_points), int(mean_points))

                # estimating the level ice draft
                # this is only for plotting/hourly level ice estimation; not stored yet
                # hourly mean level ice draft
                draft_LI = np.mean(draft_reshape, axis=1)
                dateNum_LI = np.mean(dateNum_reshape, axis=1)
                # adapt dateNum_LI to the sampling rate of 0.5Hz (it must be a multiple of 2/(3600 * 24)) (there are 3600*24 seconds per day and the unit of dateNum is days)
                dateNum_LI = np.round(dateNum_LI * 1/sample_rate * (3600 * 24)) / (1/sample_rate * (3600 * 24))
                draft_mode = np.zeros(len(draft_LI.T))
                # making a karnel PDF from the data
                for i, column in enumerate(draft_reshape):
                    if np.isclose(max(np.diff(column)), 0, atol = 1e-12):
                        x = np.linspace(min(column), max(column), 1000)
                        p = np.zeros(1000)
                    else:
                        kde = scipy.stats.gaussian_kde(column)
                        x = np.linspace(min(column), max(column), 1000)
                        p = kde(x)
                    pmax = max(p)
                    imax = np.argmax(p)
                    draft_mode[i] = x[imax]

            # rayleigh criterion
            dateNum_rc, draft_rc = rc.rayleigh_criterion(dateNum, draft)
                


            # store the data in the dictionarys (to store as json afterwards) 
            dict_draft[loc_mooring] = {'dateNum': dateNum.tolist(), 'draft': draft.tolist()}
            dict_draft_ridge[loc_mooring] = {'dateNum': dateNum_rc.tolist(), 'draft': draft_rc.tolist()}
            dict_draft_LI[loc_mooring] = {'dateNum': dateNum_LI.tolist(), 'draft': draft_LI.tolist(), 'draft_mode': draft_mode.tolist()}
        
            # store the dict in the json files (store the raw data for every location separately)
            with open(os.path.join(storage_path, f"mooring_{yr}-{yr+1}_{loc_mooring}_draft.json"), 'w') as file:
                json.dump(dict_draft, file)
        # store the dict in the json files (store the ridge and level ice data for all locations together)
        with open(os.path.join(storage_path, f"mooring_{yr}-{yr+1}_ridge.json"), 'w') as file:
            json.dump(dict_draft_ridge, file)

        with open(os.path.join(storage_path, f"mooring_{yr}-{yr+1}_LI.json"), 'w') as file:
            json.dump(dict_draft_LI, file)


    print(f"Data for draft, ridge draft and level ice draft stored in {storage_path}")
            