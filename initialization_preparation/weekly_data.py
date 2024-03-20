# get the weekly data out of the netCDF file and return them as arrays
import numpy as np
import os
from netCDF4 import Dataset

def weekly_data(years:list, locations:list, neCDF_file:str):
    """Extract the weekly data from the netCDF file and return them as arrays
    :param years: list of years to extract the data from
    :type years: list
    :param locations: list of locations to extract the data from
    :type locations: list
    :param neCDF_file: the path to the netCDF file
    :type neCDF_file: str
    :return: dictionary with the weekly data
    :rtype: dict
    """
    # open the netCDF file
    nc = Dataset(neCDF_file, 'r')
    # create the dictionary to store the weekly data
    weekly_data = {}
    # loop over the locations
    for loc in locations:
        # loop over the years
        for yr in years:
            # create the key for the dictionary
            key = f"{loc}_{yr}"
            # check if the key is already in the dictionary
            if key in weekly_data:
                print(f"Key {key} already in weekly_data")
            else:
                mean_dateNum_rc = 3600 * 24 * level_ice_statistics_days # seconds per level_ice_statistics_days unit (meaning 7 days in seconds)
                mean_points_rc = mean_dateNum_rc / dt # data points per level_ice_statistics_days unit
                no_e_rc = int(np.floor(len(dateNum)/mean_points_rc) * mean_points_rc) # number of elements to take in, so ti is dividable with number of 'mean_points' per specified 'lecel_ice_time'
                dateNum_reshape_rc = dateNum[:no_e_rc] # take only the first 'no_e' elements (meaning ignore a few last ones, such that it is reshapable)
                dateNum_reshape_rc = dateNum_reshape_rc.reshape(int(mean_points_rc), int(len(dateNum)/mean_points_rc))
                draft_reshape_rc = draft[:no_e_rc]
                draft_reshape_rc = draft_reshape_rc.reshape(int(mean_points_rc), int(len(draft)/mean_points_rc))


                # extract the data
                dateNum = nc.variables[f"{loc}_dateNum_{yr}"][:]
                draft = nc.variables[f"{loc}_draft_{yr}"][:]
                # reshape the data to weekly format
                dateNum_reshape = dateNum[:dateNum.shape[0]//7*7].reshape(-1, 7)
                draft_reshape = draft[:draft.shape[0]//7*7].reshape(-1, 7)
                # save the data in the dictionary
                weekly_data[key] = {"dateNum": dateNum_reshape, "draft": draft_reshape}
    # close the netCDF file
    nc.close()
    return weekly_data