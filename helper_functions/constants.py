# globally set constants
import os
import numpy as np

pathName_mooring_data = r"C:\Users\linasap\Documents\Ice_ridges\IceRidges_python\Data_Beaufort_Gyre_Exploration\SEASON"
pathName_dataResults = os.path.join(os.getcwd(), "Data_results")
pathName_dataRaw = os.path.join(os.getcwd(), "Data")
pathName_plots = os.path.join(os.getcwd(), "Plots")
level_ice_statistic_days = 7 # duration of sample of estimated level ice for level ice statistics (in days)
level_ice_time = 1 # duration of sample for level ice estimate (in hours)
seconds_hour = 3600 # seconds per hour
hours_day = 24 # hours per day
sampling_rate = 0.5 # sampling rate of the data in Hz
machine_precision = np.finfo(float).eps # machine precision

threshold_draft=2.5 # threshold for the rayleigh criterion
min_draft=5.0 # minimum draft for the rayleigh criterion

threshold_ridges=15 # threshold for the number of ridges per week

make_plots = True