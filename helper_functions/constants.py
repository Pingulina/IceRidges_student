# globally set constants
import os

pathName_mooring_data = r"C:\Users\linasap\Documents\Ice_ridges\IceRidges_python\Data_Beaufort_Gyre_Exploration\SEASON"
pathName_plots = os.path.join(os.getcwd(), "Plots")
level_ice_statistic_days = 7 # duration of sample of estimated level ice for level ice statistics (in days)
level_ice_time = 1 # duration of sample for level ice estimate (in hours)
seconds_hour = 3600 # seconds per hour
hours_day = 24 # hours per day

threshold_draft=2.5 # threshold for the rayleigh criterion
min_draft=5.0 # minimum draft for the rayleigh criterion

make_plots = True