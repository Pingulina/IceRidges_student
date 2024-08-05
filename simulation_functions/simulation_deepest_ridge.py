# functions to simulate the deepest ridge
import numpy as np
import numpy.matlib
import matplotlib.pyplot as plt
import os
import sys
import scipy.stats

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

def simulate_deepest_ridge(year=None, loc=None, dict_mooring_locations=None):
    """simulate the deepest ridge
    param year: int, the year for the level ice analysis
    param loc: str, the location for the level ice analysis
    param dict_mooring_locations: dict, dictionary with the mooring locations
    return None
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
    
    level_ice_deepest_mode = dict_ridge_statistics[loc]['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics[loc]['level_ice_expect_deepest_mode']
    level_ice_mode = level_ice_deepest_mode # dict_ridge_statistics[loc]['level_ice_mode'] # needs to be done
    draft_deepest_weekly_ridge = dict_ridge_statistics[loc]['draft_weekly_deepest_ridge']
    number_ridges = dict_ridge_statistics[loc]['number_ridges']
    mean_keel_draft = dict_ridge_statistics[loc]['mean_keel_draft']

    # calculations
    LI_linear_regression = np.polyfit(level_ice_mode, draft_deepest_weekly_ridge, 1)
    LI_linear_regression_fn = np.poly1d(LI_linear_regression)
    normalized_weekly_draft = draft_deepest_weekly_ridge / LI_linear_regression_fn(level_ice_mode)

    # simulate the deepest ridge
    prob_distri_normalized_weekly_draft = scipy.stats.norm.fit(normalized_weekly_draft)
    draft_deepest_weekly_ridge_simulated = LI_linear_regression_fn(level_ice_mode) * scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft, size=len(level_ice_mode))

    # repeat the simulated deepest ridge for 100 times and vary it with the distribution computed above (probabilistic approach)
    N_repeat = 100
    draft_deeply_weekest_ridge_simulated_rep = np.concatenate(numpy.matlib.repmat(LI_linear_regression_fn(level_ice_mode), 1, N_repeat)) * scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft, size=len(level_ice_mode)* N_repeat)

    # determine the return period of ridges
    N_repeat = 100000
    draft_deepest_weekly_ridge_simulated_repYears = np.concatenate(numpy.matlib.repmat(LI_linear_regression_fn(level_ice_mode), 1, N_repeat)) * scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft, size=len(level_ice_mode)* N_repeat)
    draft_deepest_weekly_ridge_simulated_repYears_sorted, exceedence_probability_simulated_repYears = exceedence_probability(draft_deepest_weekly_ridge_simulated_repYears)
    exceedence_probability_simulated_repYears = 1 - (1- exceedence_probability_simulated_repYears) ** 42

    # remove points such that minimum distance between points is 0.001
    diff_ridgeDepth = np.diff(draft_deepest_weekly_ridge_simulated_repYears_sorted)
    sum_diff = 0
    useThisPoints = []
    i = 0
    for i, thisDiff in enumerate(diff_ridgeDepth):
        sum_diff += thisDiff
        if sum_diff < 0.001:
            pass
        else:
            sum_diff = 0
            useThisPoints.append(i)
            



    draft_deepest_weekly_ridge_simulated_repYears_sorted = draft_deepest_weekly_ridge_simulated_repYears_sorted[useThisPoints]
    exceedence_probability_simulated_repYears = exceedence_probability_simulated_repYears[useThisPoints]

    draft_deepest_weekly_ridge_sorted, exceedence_probability_draft = exceedence_probability(draft_deepest_weekly_ridge)
    draft_deeply_weekest_ridge_simulated_rep_sorted, exceedence_probability_simulated_rep = exceedence_probability(draft_deeply_weekest_ridge_simulated_rep)
    ## compute the confidence intervals of the simulated deepest ridge
    # compute the percentiles of the simulated deepest ridge
    percentile_x = np.arange(len(level_ice_mode), 1, -1) / len(level_ice_mode)
    percentile_number_steps = 100000
    # initialize percentile_y
    percentile_y = np.zeros((percentile_number_steps, len(level_ice_mode)))
    # repeat draft_deepest_weekly_ridge_simulated_repYears_sorted for 100000 times with randomized factor (make a matrix)
    for i in range(percentile_number_steps):
        draft_deepest_weekly_ridge_simulated_repYears_tmp = LI_linear_regression_fn(level_ice_mode) * scipy.stats.norm.rvs(*prob_distri_normalized_weekly_draft, size=len(level_ice_mode))
        percentile_y[i, :] = np.sort(draft_deepest_weekly_ridge_simulated_repYears_tmp)
    # draft_deepest_weekly_ridge_simulated_sorted = np.sort(draft_deepest_weekly_ridge_simulated)
    # percentile_y = np.tile(draft_deepest_weekly_ridge_simulated_sorted, (percentile_number_steps, 1))

    # compute the percentiles (percentile for every week in this season)
    percentile_1 = np.percentile(percentile_y, 1, axis=0)
    percentile_5 = np.percentile(percentile_y, 5, axis=0)
    percentile_50 = np.percentile(percentile_y, 50, axis=0)
    percentile_95 = np.percentile(percentile_y, 95, axis=0)
    percentile_99 = np.percentile(percentile_y, 99, axis=0)


    #### vizualization

    # initialize the plot for tracking steps of calculations
    plt.ion() # interactive mode on to see updates of plot
    fig_overview = plt.figure(figsize=(9, 8))
    grid_spec = fig_overview.add_gridspec(3, 3)

    # plot level ice draft and weekly deepest ridge draft
    ax1 = fig_overview.add_subplot(grid_spec[0, 0])
    ax1.set_xlabel('Level ice draft [m]')
    ax1.set_ylabel('Weekly deepest keel draft [m]')
    ax1.set_xlim([0, 3])
    ax1.set_ylim([5, 30])
    ax1.scatter(level_ice_mode, draft_deepest_weekly_ridge, color='tab:blue', alpha=0.2, label='deepest ridge')
    ax1.plot(level_ice_deepest_mode, LI_linear_regression_fn(level_ice_deepest_mode), color='k', label='linear regression')
    sqrt_line_x = np.linspace(0, 3, 100)
    sqrt_line_y = 20*np.sqrt(sqrt_line_x)
    ax1.plot(sqrt_line_x, sqrt_line_y, color='k', linestyle='--')


    # plot the normalized weekly keel draft over the level ice draft
    ax2 = fig_overview.add_subplot(grid_spec[0, 1])
    ax2.set_xlabel('Level ice draft [m]')
    ax2.set_ylabel('Normalized weekly deepest keel draft [-]')
    ax2.set_xlim([0, 2])
    ax2.set_ylim([0, 2.5])
    ax2.scatter(level_ice_mode, normalized_weekly_draft, color='tab:blue', alpha=0.2, label='deepest ridge')

    # histogram of normalized weekly keel draft
    ax3 = fig_overview.add_subplot(grid_spec[0, 2])
    line_x = np.linspace(0, 2, 100)
    ax3, hist_line, plot_line, prob_distri = preliminary_analysis_plot.plot_histogram_with_line(
        ax3, normalized_weekly_draft, {'bins':20, 'color':'tab:blue', 'alpha':0.5, 'label':'deepest ridge'},
        line_x, {'distribution':'norm', 'color':'tab:blue', 'alpha':0.5, 'label':'deepest ridge'},
        'Normalized weekly deepest keel draft [-]', 'Probability density [-]', xlim=[0, 2], ylim=[0, 2.5]
        )

    # plot simulated deepest ridge over the level ice draft
    ax4 = fig_overview.add_subplot(grid_spec[1, 0])
    ax4.set_xlabel('Level ice draft [m]')
    ax4.set_ylabel('Weekly deepest keel draft [m]')
    ax4.set_xlim([0, 3])
    ax4.set_ylim([5, 30])
    ax4.set_title('Simulated deepest ridge')
    ax4.scatter(level_ice_mode, draft_deepest_weekly_ridge_simulated, color='tab:blue', alpha=0.2, label='deepest ridge')
    ax4.plot(np.linspace(0, 3, 100), LI_linear_regression_fn(np.linspace(0, 3, 100)), color='k', label='linear regression')
    sqrt_line_x = np.linspace(0, 3, 100)
    sqrt_line_y = 20*np.sqrt(sqrt_line_x)
    ax4.plot(sqrt_line_x, sqrt_line_y, color='k', linestyle='--')

    # plot exceedence probabilty of the simulated deepest ridge
    ax5 = fig_overview.add_subplot(grid_spec[1, 1])

    # make scatter plots
    ax5.set_xlabel('Weekly deepest keel draft [m]')
    ax5.set_ylabel('Exceedence probability [-]')
    ax5.set_xlim([0, 40])
    ax5.set_ylim([1e-5, 1])
    # log scale for y-axis
    ax5.set_yscale('log')
    ax5.scatter(draft_deepest_weekly_ridge_sorted, exceedence_probability_draft, color='tab:blue', s=1, label='deepest ridge')
    ax5.scatter(draft_deeply_weekest_ridge_simulated_rep_sorted, exceedence_probability_simulated_rep, color='tab:orange', s=1, label='simulated deepest ridge')
    ax5.legend()

    # make a q-q plot of the deepest ridge and the simulated deepest ridge
    ax6 = fig_overview.add_subplot(grid_spec[1, 2])
    x, y = quantil_quantil_plotData(draft_deepest_weekly_ridge, draft_deepest_weekly_ridge_simulated)
    ax6.set_xlabel('Weekly deepest keel draft [m]')
    ax6.set_ylabel('Simulated weekly deepest keel draft [m]')
    ax6.set_xlim([0, 40])
    ax6.set_ylim([0, 40])
    ax6.plot(x, y, '+', color='tab:blue', label='deepest ridge')
    ax6.plot(x, x, color='k', label='y=x')
    # ax6.legend()

    # plot the probabiltiy (every which year a ridge of this depth is expected)
    ax7 = fig_overview.add_subplot(grid_spec[2, 0])
    ax7.set_xlabel('Weekly deepest keel draft [m]')
    ax7.set_ylabel('Return period [years]')
    ax7.set_xlim([10, 50])
    ax7.set_ylim([1e-5, 1])
    ax7.set_yscale('log')
    ax7.set_yticks([1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax7.set_yticklabels(['100000', '10000', '1000', '100', '10', '1'])
    ax7.plot(draft_deepest_weekly_ridge_simulated_repYears_sorted, exceedence_probability_simulated_repYears, color='tab:blue')

    # plot confidence intervals of the simulated deepest ridge (percentiles)
    ax8 = fig_overview.add_subplot(grid_spec[2, 1])
    ax8.set_xlabel('Weekly maximum rigde keel draft [m]')
    ax8.set_ylabel('Exceedence probability [-]')
    ax8.set_xlim([5, 40])
    # log scale for y-axis
    ax8.set_yscale('log')

    counter_years = np.arange(len(level_ice_mode), 0, -1)/len(level_ice_mode)
    counter_years_2 = np.concatenate([counter_years, counter_years[::-1]])
    percentile_1_2 = np.concatenate([percentile_1, percentile_99[::-1]])
    percentile_5_2 = np.concatenate([percentile_5, percentile_95[::-1]])
    
    ax8.fill_betweenx(counter_years, percentile_1, percentile_99, color='tab:blue', alpha=0.2, label='98%')
    ax8.fill_betweenx(counter_years, percentile_5, percentile_95, color='tab:blue', alpha=0.4, label='90%')
    ax8.plot(percentile_50, counter_years, color='tab:blue', label='50\%')




def exceedence_probability(data):
    """simple computation of the exceedence probability
    param data: np.array, the data to compute the exceedence probability
    return sorted_x: np.array, the sorted data
    return exceedence_probability: np.array, the exceedence probability of the data
    """
    sorted_x = np.sort(data)
    exceedence_probability = np.linspace(len(data), 1, len(data)) / len(data)
    return sorted_x, exceedence_probability


def quantil_quantil_plotData(values1, values2):
    """returns the values needed to plot the q-q plot
    param values1: np.array, the values of the first distribution
    param values2: np.array, the values of the second distribution
    return x: np.array, the values for the x-axis
    return y: np.array, the values for the y-axis
    """
    # sort the values of the distributions
    values1_sorted = np.sort(values1)
    values2_sorted = np.sort(values2)

    return values1_sorted, values2_sorted

