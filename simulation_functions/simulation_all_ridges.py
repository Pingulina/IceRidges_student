# functions to simulate all ridge keels
import numpy as np
import numpy.matlib
import matplotlib.pyplot as plt
import os
import sys
import scipy.stats
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
constants = import_module('constants', 'helper_functions')
load_data = import_module('load_data', 'data_handling')
mooring_locs = import_module('mooring_locations', 'helper_functions')
preliminary_analysis_plot = import_module('preliminary_analysis_plot', 'plot_functions')

def simulate_all_ridges(year=None, loc=None, dict_mooring_locations=None):
    """
    Simulate all ridge keels
    """
    pathName_ridgeStatistics = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')
    
    if dict_mooring_locations is None:
        dict_mooring_locations = mooring_locs.mooring_locations(storage_path='Data') # dictionary with the mooring locations


    # get the year and location from the user, if they are not provided
    list_years = [int(season.split('-')[0]) for season in list(dict_mooring_locations.keys())]
    list_seasons = list(dict_mooring_locations.keys())

    if year is None:
        while True:
            year = int(input("Enter the year for the level ice analysis: "))
            if year in list_years:
                break
            else:
                print(f"The year {year} is not in the mooring data. Possible years are: {list_years}")
    if loc is None:    
        while True:
            loc = input("Enter the location for the level ice analysis: ")
            if loc in dict_mooring_locations[list_seasons[list_years.index(year)]].keys():
                break
            else:
                print(f"The location {loc} is not in the mooring data. Possible locations are: {list(dict_mooring_locations[list_seasons[list_years.index(year)]].keys())}")
    dateNum, draft, dict_ridge_statistics, year, loc = load_data.load_data_oneYear(path_to_json_processed=pathName_ridgeStatistics, 
                                                                                   path_to_json_mooring=path_to_json_mooring, year=year, loc=loc, 
                                                                                   skip_nonexistent_locs=True)
    
    # load the draft data of the current season
    dict_file = f"mooring_{year}-{year+1}_ridge.json"
    dict_folder = os.path.join(os.getcwd(), 'Data', 'uls_data')
    with open(os.path.join(dict_folder, dict_file)) as file:
        dict_ridge = json.load(file)
    
    level_ice_deepest_mode = np.array(dict_ridge_statistics[loc]['level_ice_deepest_mode'])
    level_ice_expect_deepest_mode = np.array(dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'])
    level_ice_mode = level_ice_deepest_mode # dict_ridge_statistics[loc]['level_ice_mode'] # needs to be done
    draft_deepest_weekly_ridge = np.array(dict_ridge_statistics[loc]['draft_weekly_deepest_ridge'])
    number_ridges = np.array(dict_ridge_statistics[loc]['number_ridges'])
    mean_keel_draft = np.array(dict_ridge_statistics[loc]['mean_keel_draft'])
    draft_rc = np.array(dict_ridge[loc]['draft'])
    dateNum_rc = np.array(dict_ridge[loc]['dateNum'])


    ### calculations
    # simulation calculations
    LI_linear_regression = np.polyfit(level_ice_mode, mean_keel_draft, 1)
    LI_linear_regression_fn = np.poly1d(LI_linear_regression)
    normalized_weekly_draft_mean = mean_keel_draft / LI_linear_regression_fn(level_ice_mode)

    # histogram calculation for normalized weekly draft mean
    number_bins_normalized_weekly_draft = 41
    hist_bins = np.linspace(0.8, 1.2, number_bins_normalized_weekly_draft)
    hist_normalized_weekly_draft, bin_edges_normalized_weekly_draft = np.histogram(normalized_weekly_draft_mean, bins=hist_bins, density=True)

    # distribution function of normalized weekly deepest keel draft
    prob_distri_normalized_weekly_draft_mean = scipy.stats.norm.fit(normalized_weekly_draft_mean)
    prob_distri_normalized_weekly_draft_mean_evaluate = scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft_mean, size=len(level_ice_mode))
    prob_distri_normalized_weekly_draft_mean_x = np.linspace(0, 2, len(level_ice_mode))





    ### vizualization
    # initialize the plot
    plt.ion() # interactive mode on to see updates of plot
    fig_overview = plt.figure(figsize=(9, 8))
    grid_spec = fig_overview.add_gridspec(5, 3)

    # plot the mean depth of ridges over level ice mode
    ax1 = fig_overview.add_subplot(grid_spec[0, 0])
    ax1.set_xlabel('Level ice draft [m]')
    ax1.set_ylabel('Weekly mean keel draft [m]')
    ax1.set_title('Mean keel draft')
    ax1.scatter(level_ice_mode, mean_keel_draft, color='blue', alpha=0.2, label='mean keel draft')
    ax1.plot(level_ice_mode, LI_linear_regression_fn(level_ice_mode), color='k', label='linear regression')

    # plot the normalized mean depth of ridges over level ice mode
    ax2 = fig_overview.add_subplot(grid_spec[0, 1])
    ax2.set_xlabel('Level ice draft [m]')
    ax2.set_ylabel('Weekly mean keel draft [m]')
    ax2.set_title('Normalized mean keel draft')
    ax2.scatter(level_ice_mode, normalized_weekly_draft_mean, color='blue', alpha=0.2, label='normalized mean keel draft')

    # plot the probability density of the normalized weekly deepest keel draft
    ax3 = fig_overview.add_subplot(grid_spec[0, 2])
    ax3.set_xlabel('Normalized weekly mean keel draft [-]')
    ax3.set_ylabel('Probability density [-]')
    ax3.set_title('Normalized mean keel draft')
    ax3.bar(bin_edges_normalized_weekly_draft[:-1], hist_normalized_weekly_draft, align='edge', color='k', alpha=0.5, zorder=0, width=(max(bin_edges_normalized_weekly_draft)-min(bin_edges_normalized_weekly_draft))/number_bins_normalized_weekly_draft)
    # plot the distribution of the normalized weekly deepest keel draft
    x = np.linspace(0.8, 1.2, 1000)
    y = scipy.stats.norm.pdf(x, np.mean(normalized_weekly_draft_mean), np.std(normalized_weekly_draft_mean))
    ax3.plot(x, y, color='red', label='normal distribution') # plot the normal distribution

    # plot the number of ridges over mean keel draft weekly
    ax4 = fig_overview.add_subplot(grid_spec[1, 0])
    ax4.set_xlabel('Weekly mean keel draft [m]')
    ax4.set_ylabel('Weekly number of ridges [-]')
    ax4.set_title('Number of ridges')
    ax4.set_xlim([5, 9])
    ax4.set_ylim([0, 1200])
    ax4.scatter(mean_keel_draft, number_ridges, color='blue', alpha=0.2, label='number of ridges')
    # some factors, described in Iljia's thesis (hopefully)
    a1 = 37.21
    b1 = 2.16
    x = np.arange(0, 9, 0.001)
    ax4.plot(x, a1 * (x-5)** b1, color='k')

    # plot normalized weekly number of ridges over weekly mean keel draft
    ax5 = fig_overview.add_subplot(grid_spec[1, 1])
    ax5.set_xlim([5, 9])
    ax5.set_ylim([0, 4])
    ax5.set_xlabel('Weekly mean keel draft [m]')
    ax5.set_ylabel('Normalized weekly number of ridges [-]')
    ax5.set_title('Normalized number of ridges')
    ax5.scatter(mean_keel_draft, number_ridges / (a1 * (mean_keel_draft-5)** b1 +1), color='blue', alpha=0.2, label='normalized number of ridges')

    # continue with plot 6,3,6 (Weibull distribution)

    print("done")


