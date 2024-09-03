# globally set constants
import os
import numpy as np

# make a dictionary with dot notation
from dotdict import Map

# dict named params, that contains all parameters
constants = Map({}) # dict() with dotdict functionality #

#constants['pathName_mooring_data'] = r"C:\Users\linasap\Documents\Ice_ridges\IceRidges_python\Data_Beaufort_Gyre_Exploration\SEASON"
constants['pathName_mooring_data'] = os.path.join(os.getcwd(), "Data_Beaufort_Gyre_Exploration", "SEASON")
constants['pathName_dataResults'] = os.path.join(os.getcwd(), "Data_results")
constants['pathName_dataRaw'] = os.path.join(os.getcwd(), "Data")
constants['pathName_plots'] = os.path.join(os.getcwd(), "Plots")
constants['level_ice_statistic_days'] = 7 # duration of sample of estimated level ice for level ice statistics (in days)
constants['level_ice_time'] = 1 # duration of sample for level ice estimate (in hours)
constants['seconds_hour'] = 3600 # seconds per hour
constants['hours_day'] = 24 # hours per day
constants['sampling_rate'] = 0.5 # sampling rate of the data in Hz
constants['machine_precision'] = np.finfo(float).eps # machine precision

constants['threshold_draft'] = 2.5 # threshold for the rayleigh criterion
constants['min_draft'] = 5.0 # minimum draft for the rayleigh criterion

constants['threshold_ridges'] = 15 # threshold for the number of ridges per week

constants['make_plots'] = True


def update_constants(new_constants):
    for key, value in new_constants.items():
        constants[key] = value
    return constants