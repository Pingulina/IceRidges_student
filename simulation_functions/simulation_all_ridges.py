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
probabilistic_helper_functions = import_module('probabilistic_helper_functions', 'plot_functions')

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
    prob_distri_normalized_weekly_draft_mean_evaluate = scipy.stats.norm.pdf(bin_edges_normalized_weekly_draft, *prob_distri_normalized_weekly_draft_mean)
    prob_distri_normalized_weekly_draft_mean_random = scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft_mean, size=len(level_ice_mode))
    prob_distri_normalized_weekly_draft_mean_x = np.linspace(0, 2, len(level_ice_mode))

    # some factors, described in Iljia's thesis (hopefully) (from plot 4)
    a1 = 37.21
    b1 = 2.16
    normalized_number_ridges = number_ridges / (a1 * (mean_keel_draft-5)** b1 +1)

    # Weibull distribution
    # fit the Weibull distribution
    prob_distri_normalized_number_ridges_x = np.linspace(0, 4, len(number_ridges))
    prob_distri_normalized_number_ridges = scipy.stats.weibull_min.fit(normalized_number_ridges, floc=0)
    prob_distri_normalized_number_ridges_evaluate = scipy.stats.weibull_min.pdf(prob_distri_normalized_number_ridges_x, *prob_distri_normalized_number_ridges)
    prob_distri_normalized_number_ridges_random = scipy.stats.weibull_min.rvs(*prob_distri_normalized_number_ridges, size=len(number_ridges))

    # histogram calculation for normalized number of ridges
    number_bins_normalized_number_ridges = 23
    hist_bins = np.linspace(0, 4, number_bins_normalized_number_ridges)
    hist_normalized_number_ridges, bin_edges_normalized_number_ridges = np.histogram(normalized_number_ridges, bins=hist_bins, density=True)

    # simulation of the weekly mean keel draft
    mean_keel_draft_simulated = LI_linear_regression_fn(level_ice_mode) * prob_distri_normalized_weekly_draft_mean_random

    # simulation of the number of ridges
    number_ridges_simulated = a1 * (mean_keel_draft-5)** b1 * prob_distri_normalized_number_ridges_random

    # normalized number of simulated ridges
    number_ridges_simulated_normalized = number_ridges_simulated / (a1 * (mean_keel_draft_simulated-5)** b1 +1)

    # main simulation
    # Monte-Carlo simulation
    mean_keel_draft_simulation = np.zeros((100, len(level_ice_mode))) # MALL (Matlab names)
    number_ridges_simulation = np.zeros((100, len(level_ice_mode)), dtype=int) # NALL
    draft_reshape_simulation = [] # Dsimsim
    for mc_index in range(100):
        mean_keel_draft_simulation[mc_index] = LI_linear_regression_fn(level_ice_mode) * scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft_mean, size=len(level_ice_mode))

        alpha = 3.444264940096133 # from matlab code
        beta = 0.294520039217058 # from matlab code

        # thickness-numberRidges relationship
        thickness_numberRidges_distribution = scipy.stats.gamma.rvs(alpha, scale=beta, size=len(level_ice_mode)) # in Matlab: R_h2n_s
        a2 = 84.69
        b2 = 1.318
        number_ridges_simulation[mc_index] = np.round(a2 * (level_ice_mode)** b2 * thickness_numberRidges_distribution).astype(int) # Nsimulated
        draft_reshape_simulation.append(np.concatenate([5 + np.random.exponential(scale = mean_keel_draft_simulation[mc_index][i] -5, size=number_ridges_simulation[mc_index][i]) for i in range(len(mean_keel_draft_simulation[mc_index]))]))
    draft_reshape_simulation = np.concatenate(draft_reshape_simulation)


    # histogram calculation for simulated ridge draft
    number_bins_draft_reshape_simulation = 71
    hist_bins = np.linspace(5, 40, number_bins_draft_reshape_simulation)
    hist_draft_reshape_simulation, bin_edges_draft_reshape_simulation = np.histogram(draft_reshape_simulation, bins=hist_bins, density=True)

    # histogram calculation for measured ridge draft
    number_bins_draft_rc = 71
    hist_bins = np.linspace(5, 40, number_bins_draft_rc)
    hist_draft_rc, bin_edges_draft_rc = np.histogram(draft_rc, bins=hist_bins, density=True)


    # do the computations for the confidence intervals
    percentile_number_steps = 100000
    # initialize percentile_mean_y
    percentile_mean_y = np.zeros((percentile_number_steps, len(level_ice_mode)))
    # repeat draft_deepest_weekly_ridge_simulated_repYears_sorted for 100000 times with randomized factor (make a matrix)
    for i in range(percentile_number_steps):
        draft_mean_weekly_ridge_simulated_repYears_tmp = LI_linear_regression_fn(level_ice_mode) * scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft_mean, size=len(level_ice_mode))
        percentile_mean_y[i, :] = np.sort(draft_mean_weekly_ridge_simulated_repYears_tmp)

    # compute the percentiles (percentile for every week in this season)
    percentile_mean_1 = np.percentile(percentile_mean_y, 1, axis=0)
    percentile_mean_5 = np.percentile(percentile_mean_y, 5, axis=0)
    percentile_mean_50 = np.percentile(percentile_mean_y, 50, axis=0)
    percentile_mean_95 = np.percentile(percentile_mean_y, 95, axis=0)
    percentile_mean_99 = np.percentile(percentile_mean_y, 99, axis=0)




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
    x = np.arange(0, 9, 0.001)
    ax4.plot(x, a1 * (x-5)** b1, color='k')

    # plot normalized weekly number of ridges over weekly mean keel draft
    ax5 = fig_overview.add_subplot(grid_spec[1, 1])
    ax5.set_xlim([5, 9])
    ax5.set_ylim([0, 4])
    ax5.set_xlabel('Weekly mean keel draft [m]')
    ax5.set_ylabel('Normalized weekly number of ridges [-]')
    ax5.set_title('Normalized number of ridges')
    ax5.scatter(mean_keel_draft, normalized_number_ridges, color='blue', alpha=0.2, label='normalized number of ridges')

    # plot normalized number of ridges histogram and weibull distribution
    ax6 = fig_overview.add_subplot(grid_spec[1, 2])
    ax6.set_xlim([0, 4])
    ax6.set_ylim([0, 1])
    ax6.set_xlabel('Normalized weekly number of ridges [-]')
    ax6.set_ylabel('Probability density [-]')
    ax6.set_title('Normalized number of ridges')
    ax6.bar(bin_edges_normalized_number_ridges[:-1], hist_normalized_number_ridges, align='edge', color='k', alpha=0.5, zorder=0, width=(max(bin_edges_normalized_number_ridges)-min(bin_edges_normalized_number_ridges))/number_bins_normalized_number_ridges)
    # plot the distribution of the normalized weekly deepest keel draft
    ax6.plot(prob_distri_normalized_number_ridges_x, prob_distri_normalized_number_ridges_evaluate, color='red', label='Weibull distribution') # plot the normal distribution

    # plot the simulated weekly mean keel draft over level ice mode
    ax7 = fig_overview.add_subplot(grid_spec[2, 0])
    ax7.set_xlim([0, 3])
    ax7.set_ylim([5, 9])
    ax7.set_xlabel('Level ice draft [m]')
    ax7.set_ylabel('Weekly mean keel draft [m]')
    ax7.set_title('Simulated mean keel draft')
    ax7.scatter(level_ice_mode, mean_keel_draft_simulated, color='blue', alpha=0.2, label='simulated mean keel draft')
    ax7.plot(level_ice_mode, LI_linear_regression_fn(level_ice_mode), color='k', label='linear regression')

    # plot the simulated weekly number of ridges over simulated weekly mean keel draft
    ax8 = fig_overview.add_subplot(grid_spec[2, 1])
    ax8.set_xlim([5, 9])
    ax8.set_ylim([0, 1200])
    ax8.set_xlabel('Weekly mean keel draft [m]')
    ax8.set_ylabel('Weekly number of ridges [-]')
    ax8.set_title('Simulated')
    ax8.scatter(mean_keel_draft_simulated, number_ridges_simulated, color='blue', alpha=0.2, label='simulated number of ridges')
    x = np.arange(0, 9, 0.001)
    ax8.plot(x, a1 * (x-5)** b1, color='k')

    # plot the simulated weekly number of ridges over the measured number of ridges
    ax9 = fig_overview.add_subplot(grid_spec[2, 2])
    ax9.set_xlabel('Measured [-]')
    ax9.set_ylabel('Simulated [-]')
    ax9.set_title('Number of ridges')
    ax9.set_yscale('log')
    draft_reshape_simulation_epp_x, draft_reshape_simulation_epp_y = probabilistic_helper_functions.exceedence_probability(draft_reshape_simulation)
    ax9.scatter(draft_reshape_simulation_epp_x, draft_reshape_simulation_epp_y, color='tab:red', label='simulated mean keel draft')
    draft_ridge_epp_x, draft_ridge_epp_y = probabilistic_helper_functions.exceedence_probability(draft_rc)
    ax9.scatter(draft_ridge_epp_x, draft_ridge_epp_y, color='tab:green', label='deepest weekly ridge')


    # plot the qq-plot of simulated weekly mean keel draft over mean keel draft
    ax10 = fig_overview.add_subplot(grid_spec[3, 0])
    ax10.set_xlabel('Measured [m]')
    ax10.set_ylabel('Simulated [m]')
    ax10.set_title('Mean keel draft')
    x, y = probabilistic_helper_functions.quantil_quantil_plotData(mean_keel_draft, mean_keel_draft_simulated)
    ax10.plot(x, y, '+', color='tab:blue', label='mean keel draft')
    ax10.plot(x, x, color='k', label='y=x')


    # plot the qq-plot simulated weekly number of ridges over the measured number of ridges
    ax11 = fig_overview.add_subplot(grid_spec[3, 1])
    ax11.set_xlabel('Measured [-]')
    ax11.set_ylabel('Simulated [-]')
    ax11.set_title('Weekly number of ridges')
    x, y = probabilistic_helper_functions.quantil_quantil_plotData(number_ridges, number_ridges_simulated)
    ax11.plot(x, y, '+', color='tab:blue', label='number of ridges')
    ax11.plot(x, x, color='k', label='y=x')


    # plot the qq-plot of all ridges depth simulation vs. measured
    ax12 = fig_overview.add_subplot(grid_spec[3, 2])
    ax12.set_xlabel('Measured [m]')
    ax12.set_ylabel('Simulated [m]')
    ax12.set_title('Ridge draft')
    x, y = probabilistic_helper_functions.quantil_quantil_plotData(draft_rc, draft_reshape_simulation)
    ax12.plot(x, y, '+', color='tab:red', label='all ridges')
    ax12.plot(x, x, color='k', label='y=x')


    # plot the normalized weekly number of ridges over the weekly mean keel draft
    ax13 = fig_overview.add_subplot(grid_spec[4, 0])
    ax13.set_xlim([5, 9])
    ax13.set_ylim([0, 4])
    ax13.set_xlabel('Weekly mean keel draft [m]')
    ax13.set_ylabel('Normalized weekly number of ridges [-]')
    ax13.set_title('Simulated')
    ax13.scatter(mean_keel_draft_simulated, number_ridges_simulated_normalized, color='blue', alpha=0.2, label='simulated number of ridges')


    # plot the histogram of the draft of all ridges and the simulated draft of all ridges
    ax14 = fig_overview.add_subplot(grid_spec[4, 1])
    ax14.set_xlim([5, 40])
    ax14.set_xlabel('Draft [m]')
    ax14.set_ylabel('Probability density [-]')
    ax14.set_title('Ridge draft')
    ax14.set_yscale('log')
    ax14.bar(bin_edges_draft_reshape_simulation[:-1], hist_draft_reshape_simulation, align='edge', color='k', alpha=0.5, zorder=0, width=(max(bin_edges_draft_reshape_simulation)-min(bin_edges_draft_reshape_simulation))/number_bins_draft_reshape_simulation, label='simulated')
    ax14.bar(bin_edges_draft_rc[:-1], hist_draft_rc, align='edge', color='tab:green', alpha=0.5, zorder=0, width=(max(bin_edges_draft_rc)-min(bin_edges_draft_rc))/number_bins_draft_rc, label='measured')


    # plot confidence intervals of the mean simulated ridge (percentiles)
    ax15 = fig_overview.add_subplot(grid_spec[4, 2])
    ax15.set_xlabel('Weekly maximum rigde keel draft [m]')
    ax15.set_ylabel('Exceedence probability [-]')
    ax15.set_xlim([0, 10])
    # log scale for y-axis
    ax15.set_yscale('log')

    counter_years = np.arange(len(level_ice_mode), 0, -1)/len(level_ice_mode)
    
    ax15.fill_betweenx(counter_years, percentile_mean_1, percentile_mean_99, color='tab:blue', alpha=0.2, label='98%')
    ax15.fill_betweenx(counter_years, percentile_mean_5, percentile_mean_95, color='tab:blue', alpha=0.4, label='90%')
    ax15.plot(percentile_mean_50, counter_years, color='tab:blue', label='50\%')


    input("Press any key to continue...")


