# parts of S003_ExtractWeeklyData.m are in this file
import numpy as np
import json
import scipy.stats
import os
import sys
from netCDF4 import Dataset, stringtochar
import pandas as pd

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


def extract_weekly_data(estimate_hourly=True, years=[2006], mooring_locations=['a', 'b', 'c', 'd'], overwrite=False, sample_rate = 0.5):
    """sort the data from the json file into weekly data and store it back to json file
    :param estimate_hourly: bool, optional, if True, the hourly data is estimated from the available data
    :param years: list, optional, list of years to be processed
    :param mooring_locations: list, optional, list of mooring locations to be processed
    :param overwrite: bool, optional, if True, the existing files are overwritten, if False, the existing files are skipped
    :param sample_rate: float, optional, sample rate of the data in Hz
    :return: None
    """

    # choose, which locations from which years should be processed 
    # TODO: choosing locations and years should be done via the GUI (table with tickboxes)
    level_ice_time = 1 # duration of sample for level ice estimate (in hours)
    level_ice_statistics_days = 7 # duration of sample of estimated level ice for level ice statistics (in days)

    dict_mooring_locations = mooring_locs.mooring_locations(storage_path='Data') # dictionary with the mooring locations

    print(f"Data from the following seasons was found and will be processed by default: {dict_mooring_locations.keys()}")
    change_default_seasons = input("Do you want to change the default seasons? - Y/y, N/n:")
    if change_default_seasons == 'Y' or change_default_seasons == 'y':
        change_seasons = input("Enter the seasons to be processed (separated by a comma), format: start_year-end_year: ").split(',')
        for season in change_seasons:
            if season not in dict_mooring_locations:
                print(f"Season {season} not found in the data.")
                change_seasons.remove(season)
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


    # the data should be stored in a netCDF file
    # make a netCDF file to store the data
    storage_path = os.path.join('Data')
    file_storage = os.path.join(storage_path, 'raw_and_rayleigh_data.nc')
    # create the root group (parental group to all data groups)
    rootgrp = Dataset(file_storage, 'w', format='NETCDF4')

    # create the dimensions
    time = rootgrp.createDimension('time', None)
    time_ridge = rootgrp.createDimension('time_ridge', None)
    time_LI = rootgrp.createDimension('time_LI', None)
    # latitude = rootgrp.createDimension('lat', None)
    # longitude = rootgrp.createDimension('lon', None)
    position = rootgrp.createDimension('pos', None)

    # create the coordinate variables
    times = rootgrp.createVariable('time', 'f8', ('time',)) # f8 is a float of 8 bytes (float64)
    times_ridges = rootgrp.createVariable('time_ridges', 'f8', ('time_ridge',))
    times_LI = rootgrp.createVariable('time_LI', 'f8', ('time_LI',))
    # latitudes = rootgrp.createVariable('lat', 'f4', ('lat',)) # f4 is a float of 4 bytes (float32)
    # longitudes = rootgrp.createVariable('lon', 'f4', ('lon',))
    positions = rootgrp.createVariable('pos', 'S1', ('pos',))
    times.units = 'days since 0001-01-01 00:00:00'
    times.calendar = 'gregorian'
    times_ridges.units = 'days since 0001-01-01 00:00:00'
    times_ridges.calendar = 'gregorian'
    # latitudes.units = 'degrees north'
    # longitudes.units = 'degrees east'
    positions.units = 'position key'


    # iterate over the mooring locations and years and process the data

    for mooring_period in dict_mooring_locations:
        yr = int(mooring_period.split('-')[0])
        # initialize a pandas dataframe to store the data for all mooring locations. This is done, since the time of the measured ridges and level ice differs for all moorings, but a commont time vector is needed for the netCDF file
        draft_df = pd.DataFrame()
        for loc_mooring in dict_mooring_locations[mooring_period]:

    
            print(f"Processing the location {loc_mooring} for the season {yr}-{yr+1}")
            # load the data from the dat file and store it in a dict
            data_dict = d2d.data2dict(os.path.join(os.getcwd(), 'Data_Beaufort_Gyre_Exploration_Project', mooring_period), f"uls{mooring_period[2:4]}{loc_mooring}_draft.dat")
            # remove date and time from the dict
            data_dict.pop('date')
            data_dict.pop('time')
            # meaning only keep position_info, dateNum and draft
            dateNum = np.array(data_dict['dateNum'])
            draft = np.array(data_dict['draft'])
            # fit dateNum to sample rate (full seconds)
            dateNum = np.round(dateNum * 1/sample_rate * (3600 * 24)) / (1/sample_rate * (3600 * 24))

            lon = dict_mooring_locations[mooring_period][loc_mooring]['lon']
            lat = dict_mooring_locations[mooring_period][loc_mooring]['lat']
            

            

            # mean time interval between two measurements
            dt_days = np.mean(np.diff(dateNum)) # time step in dateNum format (days)            
            # if there is a missmatch in the data time, fix it
            if not np.isclose(min(np.diff(dateNum)), dt_days, atol=1e-8):
                print("There is a missmatch in the time data. Fixing it automatically.")
                dateNum = np.arange(dateNum[0], dateNum[-1], dt_days)
            # transform dt_days in seconds
            hours_day = 24
            seconds_hour = 3600
            dt = np.round(dt_days * hours_day * seconds_hour) # FIXME: this is a restriction that only natural numbers are allowed for dt

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
                # this is only for plotting/hourly level ice estimation; not stored yet
                # hourly mean level ice draft
                draft_LI = np.mean(draft_reshape, axis=0)
                dateNum_LI = np.mean(dateNum_reshape, axis=0)
                # adapt dateNum_LI to the sampling rate of 0.5Hz (it must be a multiple of 2/(3600 * 24)) (there are 3600*24 seconds per day and the unit of dateNum is days)
                dateNum_LI = np.round(dateNum_LI * 1/sample_rate * (3600 * 24)) / (1/sample_rate * (3600 * 24))
                draft_mode = np.zeros(len(draft_LI))
                # making a karnel PDF from the data
                for i, column in enumerate(draft_reshape.T):
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
            
            



            dateNum_rc, draft_rc = rc.rayleigh_criterion(dateNum, draft, threshold_draft=2.5, min_draft=5.0)
                

            # Ridge statistics
            # transferring the time vector in a matrix dateTime_reshape_rc with N columns (weeks)
            mean_dateNum_rc = 3600 * 24 * level_ice_statistics_days # seconds per level_ice_statistics_days unit (meaning 7 days in seconds)
            mean_points_rc = mean_dateNum_rc / dt # data points per level_ice_statistics_days unit
            no_e_rc = int(np.floor(len(dateNum)/mean_points_rc) * mean_points_rc) # number of elements to take in, so ti is dividable with number of 'mean_points' per specified 'lecel_ice_time'
            dateNum_reshape_rc = dateNum[:no_e_rc] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
            dateNum_reshape_rc = dateNum_reshape_rc.reshape(int(mean_points_rc), int(len(dateNum)/mean_points_rc))
            draft_reshape_rc = draft[:no_e_rc]
            draft_reshape_rc = draft_reshape_rc.reshape(int(mean_points_rc), int(len(draft)/mean_points_rc))

            # store dateNum_reshape_rc in dict_weekly_data with key loc_mooring and yr
            # dict_weekly_data[f"{loc_mooring}_{yr}"] = {'dateNum_reshape': dateNum_reshape.tolist(), 'dateNum_reshape_rc': dateNum_reshape_rc.tolist(), 'draft_reshape': draft_reshape.tolist(), 'draft_reshape_rc': draft_reshape_rc.tolist(), 'dateNum_LI': dateNum_LI.tolist(), 'draft_LI': draft_LI.tolist(), 'draft_mode': draft_mode.tolist()}
            
            
            # add dateNum in the first column of the draft_df
            if draft_df.empty:
                draft_df['dateNum'] = dateNum
            else:
                # add all values of dateNum to the draft_df, if they are not already in the draft_df
                tempDateNum = []
                for date in dateNum:
                    if date not in draft_df['dateNum']:
                        tempDateNum.append(date)
                tempDf = pd.DataFrame(tempDateNum, columns=['dateNum'])
                draft_df = pd.concat([draft_df, tempDf])
                # sort the draft_df by dateNum
                draft_df = draft_df.sort_values(by='dateNum')
                # reset the index of the draft_df
                draft_df = draft_df.reset_index(drop=True)
            # add the draft values to the draft_df
            ############################# THE SAMPLE RATE OF ALL NATIVE DATA MUST BE THE SAME ##############################################
            idx_draft_start = np.where(draft_df['dateNum'] == dateNum[0])[0][0]
            idx_draft_end = np.where(draft_df['dateNum'] == dateNum[-1])[0][0]
            # add the draft values to the draft_df in column f"draft_{loc_mooring}" between idx_draft_start and idx_draft_end
            draft_df[f"draft_{loc_mooring}"] = np.nan
            draft_df.loc[idx_draft_start:idx_draft_end+1, f"draft_{loc_mooring}"] = draft

            # add the draft_rc values to the draft_df (the sample rate is unknown, so every value needs to get its index)
            draft_df[f"draft_rc_{loc_mooring}"] = np.nan
            for i, date in enumerate(dateNum_rc):
                idx = np.where(draft_df['dateNum'] == date)[0]
                draft_df.loc[idx, f"draft_rc_{loc_mooring}"] = draft_rc[i]

            # add the draft_LI values to the draft_df (the sample rate is unknown, so every value needs to get its index)
            draft_df[f"draft_LI_{loc_mooring}"] = np.nan
            for i, date in enumerate(dateNum_LI):
                # find where the nearest date is in the draft_df (distance is half the reciprocal of the sample rate mltiplied by the ratio of seconds per day)
                idx = np.where(np.abs(draft_df['dateNum'] - date) < 1/(3600*24*sample_rate*2))[0]
                draft_df.loc[idx, f"draft_LI_{loc_mooring}"] = draft_LI[i]



            # add values to the coordinate variables (append, if the variable already exists and the current value is not in the list)
            # if times[:] == []: # if the variable is empty, add the first value
            #     times[:] = dateNum
            #     times_ridges[:] = dateNum_rc
            #     times_LI[:] = dateNum_LI
            if not (dateNum[0] in times[:] and dateNum[-1] in times[:]): # if the first and last value are not in the list, add the values
                times[:] = np.append(times[:], dateNum)
                times_ridges[:] = np.append(times_ridges[:], dateNum_rc)
                times_LI[:] = np.append(times_LI[:], dateNum_LI)
            else:
                pass # if the value is already in the list, do nothing

            # if positions == []:
            #     positions[:] = loc_mooring
            if loc_mooring not in positions[:]:
                positions[:] = np.append(positions[:], loc_mooring)
            else:
                pass # if the value is already in the list, do nothing

            # get the indices of the values in the coordinate variables
            idx_time_start = np.where(times[:] == dateNum[0])[0][0]
            idx_time_end = np.where(times[:] == dateNum[-1])[0][0]
            idx_time_ridge_start = np.where(times_ridges[:] == dateNum_rc[0])[0][0]
            idx_time_ridge_end = np.where(times_ridges[:] == dateNum_rc[-1])[0][0]
            idx_time_LI_start = np.where(times_LI[:] == dateNum_LI[0])[0][0]
            idx_time_LI_end = np.where(times_LI[:] == dateNum_LI[-1])[0][0]
            idx_pos = np.where(positions[:] == stringtochar(np.array([loc_mooring],'S1')))[0][0]


            # create variable for the native data
            draft_native = rootgrp.createVariable('draft', 'f4', ('time', 'pos')) # 'lat','lon',))
            # add values to the variable
            draft_native[idx_time_start:idx_time_end+1, idx_pos] = draft


            # create variable for ridge data (rayleigh criterion)
            draft_ridge = rootgrp.createVariable('draft_rc', 'f4', ('time_ridge','pos')) # 'lat','lon',))
            # add values to the variable
            draft_ridge[idx_time_ridge_start:idx_time_ridge_end+1, idx_pos] = draft_rc

            # create variable for level ice data
            draft_levelIce = rootgrp.createVariable('draft_LI', 'f4', ('time_LI','pos')) #'lat','lon',))
            # add values to the variable
            draft_levelIce[idx_time_LI_start:idx_time_LI_end+1, idx_pos] = draft_LI



            # TODO: what about the draft mode? It is not clear, where it should be stored

            
        # store the draft_df in the netCDF file

    rootgrp.close()

            
    # store the weekly data in a json file
    # storage_name = f"mooring_{years[0]}-{years[-1]}.json"
    storage_name = f"mooring_{years[0]}-{years[-1]}.nc"
    storage_path = os.path.join('Data', 'weekly_data')
    file_storage = os.path.join(storage_path, storage_name)
    # if the storage path does not exist, create it
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    weekly_data_nc = Dataset(file_storage, 'w', format='NETCDF4')

    # for every location, the data should be stored in a separate group
    # store the data from dict_weekly_data in the netCDF file
    

    with open(file_storage, 'w') as file:
        json.dump(dict_weekly_data, file)

    print(f"Weekly data stored in {file_storage}")
            