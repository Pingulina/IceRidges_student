# stuff from S006

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
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
prelim_plot = import_module('preliminary_analysis_plot', 'plot_functions')
load_data = import_module('load_data', 'data_handling')


def prelim_analysis_simulation(years, locs):
    """ decription of the function
    """
    # check, if the years and locations are lists, if not, make lists
    if isinstance(years, list):
        pass
    elif isinstance(years, int):
        years = [years]
    else:
        raise ValueError("The input years must be a list or an integer.")
    if isinstance(locs, list):
        pass
    elif isinstance(locs, str):
        locs = [locs]
    else:
        raise ValueError("The input locations must be a list or a string.")
    
    # load the data
    pathName = os.getcwd()
    path_to_json_mooring = os.path.join(pathName, 'Data', 'uls_data')
    path_to_json_corrected = os.path.join(constants.pathName_dataResults, 'ridge_statistics', 'ridge_statistics_corrected')
    path_to_json_processed = os.path.join(constants.pathName_dataResults, 'ridge_statistics')

    level_ice_deepest_mode = []
    mean_keel_draft = []
    number_of_ridges = []
    draft_weekly_deepest_ridge = []
    for year in years:
        for loc in locs:
            # check, if this year and location exists in the corrected files, otherwise use the processed files
            fileName = f"ridge_statistics_{year}{loc}.json"
            if os.path.exists(os.path.join(path_to_json_corrected, fileName)):
                dateNum, draft, dict_ridge_statistics_corrected, year, loc = load_data.load_data_oneYear(path_to_json_processed=path_to_json_corrected, path_to_json_mooring=path_to_json_mooring,
                                                                                             year=year, loc=loc)
            else:
                dateNum, draft, dict_ridge_statistics_corrected, year, loc = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, path_to_json_mooring=path_to_json_mooring,
                                                                                             year=year, loc=loc, skip_nonexistent_locs=True)
                if dateNum is None:
                    continue
            week_to_keep = dict_ridge_statistics_corrected[loc]['week_to_keep']
            # make lists of the data, include all data that is marked to keep (listed in week_to_keep)
            level_ice_deepest_mode.extend([dict_ridge_statistics_corrected[loc]['level_ice_deepest_mode'][weekNr] for weekNr in np.where(week_to_keep)[0]]) # needs to be this way, because dict entry is a list not a np.array
            mean_keel_draft.extend([dict_ridge_statistics_corrected[loc]['mean_keel_draft'][weekNr] for weekNr in np.where(week_to_keep)[0]])
            number_of_ridges.extend([dict_ridge_statistics_corrected[loc]['number_ridges'][weekNr] for weekNr in np.where(week_to_keep)[0]])
            draft_weekly_deepest_ridge.extend([dict_ridge_statistics_corrected[loc]['deepest_ridge'][weekNr] for weekNr in np.where(week_to_keep)[0]])

    # make numpy arrays
    level_ice_deepest_mode = np.array(level_ice_deepest_mode)
    mean_keel_draft = np.array(mean_keel_draft)
    number_of_ridges = np.array(number_of_ridges)
    draft_weekly_deepest_ridge = np.array(draft_weekly_deepest_ridge)
    
    # make a figure with subplot grid (3 columns, 6 rows)
    plt.ion()
    figure_prelim_analysis = plt.figure(layout='constrained', figsize=(8,8)) # 4/5 aspect ratio
    gridspec_prelim_analysis = figure_prelim_analysis.add_gridspec(6,3)
    figure_prelim_analysis.suptitle(f"Preliminary analysis", fontsize=16)

    # figure measured mean ridge keel depth vs level ice deepest mode
    ax_data_ridgeDepth_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[0, 0])
    # curve fitting
    line_x = np.linspace(0, 3, 100)
    line_y, b = curve_fitting(level_ice_deepest_mode, mean_keel_draft, line_x)
    ax_data_ridgeDepth_LIDM, scatter_data_ridgeDepth_LIDM, line_data_ridgeDepth_LIDM = prelim_plot.plot_scatter_with_line(
        ax_data_ridgeDepth_LIDM, level_ice_deepest_mode, mean_keel_draft, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x, line_y, {'color':'tab:red'}, 'LI_DM [m]', 'Mean ridge keel depth [m]', xlim=[0, 3], ylim=[5, 9], title="Data")

    # figure some probabilty distribution M/regression?
    ax_ridgeDepth_probDist = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[0, 1])
    regression_ridgeDepth = np.divide(mean_keel_draft, fitting_y(level_ice_deepest_mode, b))
    line_x = np.arange(0.79, 1.2, 0.02)
    ax_ridgeDepth_probDist, hist_ridgeDepth_probDist, line_ridgeDepth_probDist, ridgeDepth_probDist = prelim_plot.plot_histogram_with_line(
        ax_ridgeDepth_probDist, regression_ridgeDepth, {'color':'tab:blue', 'bins':20}, line_x, {'color':'tab:red'}, 
        'normalized mean keel depth', 'Probabitly distribution', xlim=[0.8, 1.2])


    # figure simulated mean ridge keel depth vs level ice deepest mode
    ax_sim_ridgeDepth_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[0, 2])
    # curve fitting
    line_x = np.linspace(0, 3, 100)
    line_y, b = curve_fitting(level_ice_deepest_mode, mean_keel_draft, line_x)
    random_numbers = np.random.normal(ridgeDepth_probDist[0], ridgeDepth_probDist[1], len(mean_keel_draft))
    ax_sim_ridgeDepth_LIDM, scatter_sim_ridgeDepth_LIDM, line_sim_ridgeDepth_LIDM = prelim_plot.plot_scatter_with_line(
        ax_sim_ridgeDepth_LIDM, level_ice_deepest_mode, fitting_y(level_ice_deepest_mode, b) * random_numbers, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5},
        line_x, line_y, {'color':'tab:red'}, 'LI_DM [m]', 'Mean ridge keel depth [m]', xlim=[0, 3], ylim=[5, 9], title="Simulated")
    

    # figure number of ridges over measured level ice deepest mode
    ax_data_ridgeNumber_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[1, 0])
    # make scatter plot with line
    line_x = np.linspace(0, 5, 100)
    line_y = 84.69* line_x ** 1.318 # why??? This is in Ilja's code

    ax_data_ridgeNumber_LIDM, scatter_data_ridgeNumber_LIDM, line_data_ridgeNumber_LIDM = prelim_plot.plot_scatter_with_line(
        ax_data_ridgeNumber_LIDM, level_ice_deepest_mode, number_of_ridges, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x, line_y, {'color':'tab:red'}, 'LI_DM [m]', 'Number of ridges', xlim=[0, 5], ylim=[5, 1200], title="Data")


    # figure more thickness over level ice deepest mode?
    ax_ridgeNumber_probDist = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[1, 1])

    # figure data number of ridges over mean keel draft
    ax_data_ridgeNumber_ridgeDepth = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[2,0])
    # curve fitting
    line_x = np.arange(0, 5, 0.001)
    line_y = 38.78 * line_x ** 2.047 # why??? This is in Ilja's code
    ax_data_ridgeNumber_ridgeDepth, scatter_data_ridgeNumber_ridgeDepth, line_data_ridgeNumber_ridgeDepth = prelim_plot.plot_scatter_with_line(
        ax_data_ridgeNumber_ridgeDepth, mean_keel_draft, number_of_ridges, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x+5, line_y, {'color':'tab:red'}, 'Mean keel draft [m]', 'Number of ridges', xlim=[constants.min_draft, 10], ylim=[5, 1200], title="Data")
    
    # figure probabiltiy distribution number of ridges
    ax_ridgeNumber_probDist = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[2, 1])
    regression_ridgeNumber = np.divide(number_of_ridges, 38.78 * (mean_keel_draft-constants.min_draft) ** 2.047)
    line_x = np.arange(0, 3, 0.01)
    ax_ridgeNumber_probDist, hist_ridgeNumber_probDist, line_ridgeNumber_probDist, ridgeNumber_probDist = prelim_plot.plot_histogram_with_line(
        ax_ridgeNumber_probDist, regression_ridgeNumber, {'color':'tab:blue', 'bins':20}, line_x, {'color':'tab:red', 'distribution':'nakagami'}, 
        'normalized number of ridges', 'Probabitly distribution', xlim=[0, 3])

    # figure simulated number of ridges over mean keel draft
    ax_sim_ridgeNumber_ridgeDepth = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[2,2])
    # curve fitting
    line_x = np.arange(0, 5, 0.001)
    line_y = 38.78 * line_x ** 2.047 # why??? This is in Ilja's code
    number_of_ridges_sim = 38.78 * (mean_keel_draft-constants.min_draft) ** 2.047 * np.random.normal(ridgeNumber_probDist[0], ridgeNumber_probDist[1], len(mean_keel_draft))
    ax_sim_ridgeNumber_ridgeDepth, scatter_sim_ridgeNumber_ridgeDepth, line_sim_ridgeNumber_ridgeDepth = prelim_plot.plot_scatter_with_line(
        ax_sim_ridgeNumber_ridgeDepth, mean_keel_draft, number_of_ridges_sim, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x+5, line_y, {'color':'tab:red'}, 'Mean keel draft [m]', 'Number of ridges', xlim=[constants.min_draft, 10], ylim=[5, 1200], title="Simulated")
    
    # figure exceedence probability over number of ridges
    ax_exceedence_prob_ridgeNumber = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[3,0])
    # make the y-scale logarithmic
    ax_exceedence_prob_ridgeNumber.set_yscale('log')
    scatter_x = np.sort(regression_ridgeNumber)
    scatter_y = np.arange(len(scatter_x), 0, -1) / len(scatter_x)
    line_x = np.arange(0, 3, 0.01)
    line_y = 1- scipy.stats.nakagami.cdf(line_x, ridgeNumber_probDist[0], ridgeNumber_probDist[1])
    ax_exceedence_prob_ridgeNumber, scatter_exceedence_prob_ridgeNumber, line_exceedence_prob_ridgeNumber = prelim_plot.plot_scatter_with_line(
        ax_exceedence_prob_ridgeNumber, scatter_x, scatter_y, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x, line_y, {'color':'tab:red'}, 'normalized number of ridges', 'Exceedence probability', xlim=[0, 3], ylim=[1e-4, 1], title="Data")

    # figure normalized number of ridges ove mean keel draft
    ax_ridgeNumber_ridgeDepth = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[3,1])
    ax_ridgeNumber_ridgeDepth, scatter_ridgeNumber_ridgeDepth = prelim_plot.plot_scatter(
        ax_ridgeNumber_ridgeDepth, mean_keel_draft, regression_ridgeNumber, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5},
        'Mean keel draft [m]', 'normalized number of ridges', xlim=[constants.min_draft, 10], ylim=[0, 5], title="Data")

    # figure simulated number of ridges over level ice deepest mode
    ax_sim_ridgeNumber_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[3,2])
    ax_sim_ridgeNumber_LIDM, scatter_sim_ridgeNumber_LIDM = prelim_plot.plot_scatter(
        ax_sim_ridgeNumber_LIDM, level_ice_deepest_mode, number_of_ridges_sim, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        'LI_DM [m]', 'Number of ridges', xlim=[0, 5], ylim=[0, 1200], title="Simulated")
    
    # simulation keel depth
    mean_keel_draft_simulated = curve_fitting(level_ice_deepest_mode, mean_keel_draft, level_ice_deepest_mode)[0] * np.random.normal(ridgeDepth_probDist[0], ridgeDepth_probDist[1], len(mean_keel_draft))
    number_of_ridges_simByDraft = 38.78 * (mean_keel_draft_simulated-constants.min_draft) ** 2.047 * np.random.normal(ridgeNumber_probDist[0], ridgeNumber_probDist[1], len(mean_keel_draft_simulated))
    # exceedance probability of keel depth (depths of all keys)
    weeks_to_keep = dict_ridge_statistics_corrected[loc]['week_to_keep']
    keel_draft_ridge_toKeep = np.concatenate([dict_ridge_statistics_corrected[loc]['keel_draft_ridge'][weekNr] for weekNr in np.where(weeks_to_keep)[0]])
    scatter1_x = np.sort(keel_draft_ridge_toKeep)
    scatter1_y = np.arange(len(scatter1_x), 0, -1) / len(scatter1_x)

    keel_draft_ridge_toKeep_sim = np.concatenate([5 + np.random.exponential(mean_keel_draft_simulated[weekNr] - 5, int(np.ceil(number_of_ridges_simByDraft[weekNr]))) for weekNr in range(len(mean_keel_draft_simulated))])
    keel_draft_ridge_toKeep_max_sim = np.array([max(5 + np.random.exponential(mean_keel_draft_simulated[weekNr] - 5, int(np.ceil(number_of_ridges_simByDraft[weekNr])))) for weekNr in np.where(weeks_to_keep)[0]])
    scatter2_x = np.sort(keel_draft_ridge_toKeep_sim)
    scatter2_y = np.arange(len(scatter2_x), 0, -1) / len(scatter2_x)

    # figure exceedence probablity over keel depth
    ax_exceedence_prob_ridgeDepth = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[4,0])
    ax_exceedence_prob_ridgeDepth.set_yscale('log')
    
    ax_exceedence_prob_ridgeDepth, scatter_exceedence_prob_ridgeDepth_data, scatter_exceedence_prob_ridgeDepth_sim = prelim_plot.plot_scatter_double(
        ax_exceedence_prob_ridgeDepth, scatter1_x, scatter1_y, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        scatter2_x, scatter2_y, {'color':'tab:red', 'marker':'o', 's':6, 'alpha':0.5}, 'Keel depth [m]', 'Exceedence probability', xlim=[0, 40])



    # figure keel depth probability denstiy
    ax_probDens_ridgeDepth = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[4,1])
    ax_probDens_ridgeDepth.set_yscale('log')
    ax_probDens_ridgeDepth, hist_probDens_ridgeDepth_data, hist_probDens_ridgeDepth_sim = prelim_plot.plot_histogram_double(
        ax_probDens_ridgeDepth, keel_draft_ridge_toKeep, {'color':'tab:blue', 'bins':30, 'density':True}, keel_draft_ridge_toKeep_sim, {'color':'tab:red', 'bins':30, 'density':True},
        'Keel depth [m]', 'Probability density')
    
    # figure probabiltiy density over keel depth
    
    # figure weekly deepest keel over level ice deepest mode
    ax_weekly_deepest_keel_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[5,0])
    line_x = np.arange(0, 4, 1)
    line_y, bb = curve_fitting(level_ice_deepest_mode, draft_weekly_deepest_ridge, line_x)
    ax_weekly_deepest_keel_LIDM, scatter_weekly_deepest_keel_LIDM, line_weekly_deepest_keel_LIDM = prelim_plot.plot_scatter_with_line(
        ax_weekly_deepest_keel_LIDM, level_ice_deepest_mode, draft_weekly_deepest_ridge, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x, line_y, {'color':'tab:red'}, 'LI_DM [m]', 'Weekly deepest keel [m]', xlim=[0, 4], ylim=[5, 9], title="Data")

    # figure simulated weekly deepest keel over level ice deepest mode
    ax_sim_weekly_deepest_keel_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[5,1])
    line_x = np.arange(0, 4, 1)
    line_y, bb = curve_fitting(level_ice_deepest_mode, keel_draft_ridge_toKeep_max_sim, line_x)
    ax_sim_weekly_deepest_keel_LIDM, scatter_sim_weekly_deepest_keel_LIDM, line_sim_weekly_deepest_keel_LIDM = prelim_plot.plot_scatter_with_line(
        ax_sim_weekly_deepest_keel_LIDM, level_ice_deepest_mode, keel_draft_ridge_toKeep_max_sim, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x, line_y, {'color':'tab:red'}, 'LI_DM [m]', 'Weekly deepest keel [m]', xlim=[0, 4], ylim=[5, 9], title="Simulated")

    # figure weekly deepest keel simulated over measured
    ax_weekly_deepest_keel_sim_data = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[5,2])


    print('some stuff')

    



def curve_fitting(data_x, data_y, fit_x):
    """ curve fitting on the data set data_x, data_y
    :param data_x: x values of the data set
    :param data_y: y values of the data set
    :param fitting_x: x values for the curve fitting
    :return: fitting_y: y values for the curve fitting
    :return: b: coefficients of the linear fit
    """
    matrix_x = np.vstack([data_x, np.ones(len(data_x))]).T
    b = np.linalg.lstsq(matrix_x, data_y, rcond=None)[0]
    fit_y = fitting_y(fit_x, b)
    return fit_y, b

def fitting_y(x, b):
    """ linear fitting function
    :param x: x values
    :param b: coefficients of the linear fit
    :return: y values
    """
    if type(x) == list:
        x = np.array(x)
    return b[0]*x + b[1]