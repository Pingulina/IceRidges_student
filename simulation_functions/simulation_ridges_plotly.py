# functions to simulate the deepest ridge
import numpy as np
import numpy.matlib
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
probabilistic_helper_functions = import_module('probabilistic_helper_functions', 'plot_functions')
j2d = import_module('jsonified2dict', 'data_handling')



def simulate_deepest_ridge(dict_ridge_statistics_jsonified):
    """simulate the deepest ridge
    param year: int, the year for the level ice analysis
    param loc: str, the location for the level ice analysis
    param dict_mooring_locations: dict, dictionary with the mooring locations
    return None
    """
    dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified) # this is to convert the jsonified data to a dict with its original data types
    dateNum_LI = dict_ridge_statistics['dateNum_LI']
    draft_LI = dict_ridge_statistics['draft_LI']
    draft_mode = dict_ridge_statistics['draft_mode']
    dateNum_rc = dict_ridge_statistics['dateNum_rc']
    draft_rc = dict_ridge_statistics['draft_rc']
    dateNum_rc_pd = dict_ridge_statistics['mean_dateNum']
    draft_deepest_ridge = dict_ridge_statistics['expect_deepest_ridge']
    level_ice_deepest_mode = dict_ridge_statistics['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics['level_ice_expect_deepest_mode']
    week_to_keep = dict_ridge_statistics['week_to_keep']  # must be int
    number_ridges = dict_ridge_statistics['number_ridges']
    mean_keel_draft = dict_ridge_statistics['mean_keel_draft']
    draft_max_weekly = dict_ridge_statistics['draft_weekly_deepest_ridge']
    dateNum_reshape = dict_ridge_statistics['keel_dateNum']
    draft_reshape = dict_ridge_statistics['keel_draft']
    draft_ridge = dict_ridge_statistics['keel_draft_ridge']
    dateNum_ridge = dict_ridge_statistics['keel_dateNum_ridge']

    week_starts = dict_ridge_statistics['week_start']
    week_ends = dict_ridge_statistics['week_end']

    peaks_location = dict_ridge_statistics['peaks_location']
    peaks_intensity = dict_ridge_statistics['peaks_intensity']

    dateNum = dict_ridge_statistics['dateNum']
    draft = dict_ridge_statistics['draft']
    
 
    level_ice_mode = level_ice_deepest_mode # dict_ridge_statistics[loc]['level_ice_mode'] # needs to be done
    draft_deepest_weekly_ridge = dict_ridge_statistics['draft_weekly_deepest_ridge']


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
    draft_deepest_weekly_ridge_simulated_repYears_sorted, exceedence_probability_simulated_repYears = probabilistic_helper_functions.exceedence_probability(draft_deepest_weekly_ridge_simulated_repYears)
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

    draft_deepest_weekly_ridge_sorted, exceedence_probability_draft = probabilistic_helper_functions.exceedence_probability(draft_deepest_weekly_ridge)
    draft_deeply_weekest_ridge_simulated_rep_sorted, exceedence_probability_simulated_rep = probabilistic_helper_functions.exceedence_probability(draft_deeply_weekest_ridge_simulated_rep)
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

    # # compute the percentiles (percentile for every week in this season)
    # percentile_1 = np.percentile(percentile_y, 1, axis=0)
    # percentile_5 = np.percentile(percentile_y, 5, axis=0)
    # percentile_50 = np.percentile(percentile_y, 50, axis=0)
    # percentile_95 = np.percentile(percentile_y, 95, axis=0)
    # percentile_99 = np.percentile(percentile_y, 99, axis=0)

    return prob_distri_normalized_weekly_draft, LI_linear_regression_fn, percentile_x, percentile_y, exceedence_probability_draft, exceedence_probability_simulated_rep


def simulate_all_ridges(dict_ridge_statistics_jsonified):
    """
    Simulate all ridge keels
    """
    dict_ridge_statistics = j2d.jsonified2dict(dict_ridge_statistics_jsonified) # this is to convert the jsonified data to a dict with its original data types
    dateNum_LI = dict_ridge_statistics['dateNum_LI']
    draft_LI = dict_ridge_statistics['draft_LI']
    draft_mode = dict_ridge_statistics['draft_mode']
    dateNum_rc = dict_ridge_statistics['dateNum_rc']
    draft_rc = dict_ridge_statistics['draft_rc']
    dateNum_rc_pd = dict_ridge_statistics['mean_dateNum']
    draft_deepest_ridge = dict_ridge_statistics['expect_deepest_ridge']
    level_ice_deepest_mode = dict_ridge_statistics['level_ice_deepest_mode']
    level_ice_expect_deepest_mode = dict_ridge_statistics['level_ice_expect_deepest_mode']
    week_to_keep = dict_ridge_statistics['week_to_keep']  # must be int
    number_ridges = dict_ridge_statistics['number_ridges']
    mean_keel_draft = dict_ridge_statistics['mean_keel_draft']
    draft_max_weekly = dict_ridge_statistics['draft_weekly_deepest_ridge']
    dateNum_reshape = dict_ridge_statistics['keel_dateNum']
    draft_reshape = dict_ridge_statistics['keel_draft']
    draft_ridge = dict_ridge_statistics['keel_draft_ridge']
    dateNum_ridge = dict_ridge_statistics['keel_dateNum_ridge']

    week_starts = dict_ridge_statistics['week_start']
    week_ends = dict_ridge_statistics['week_end']

    peaks_location = dict_ridge_statistics['peaks_location']
    peaks_intensity = dict_ridge_statistics['peaks_intensity']

    dateNum = dict_ridge_statistics['dateNum']
    draft = dict_ridge_statistics['draft']
    
 
    level_ice_mode = level_ice_deepest_mode # dict_ridge_statistics[loc]['level_ice_mode'] # needs to be done
    draft_deepest_weekly_ridge = dict_ridge_statistics['draft_weekly_deepest_ridge']
    

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

    return prob_distri_normalized_weekly_draft_mean_evaluate, prob_distri_normalized_number_ridges_evaluate, percentile_mean_y, LI_linear_regression_fn
