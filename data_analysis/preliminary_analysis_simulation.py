# stuff from S006

import numpy as np
import sys
import os
import matplotlib.pyplot as plt



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
    for year in years:
        for loc in locs:
            # check, if this year and location exists in the corrected files, otherwise use the processed files
            fileName = f"ridge_statistics_{year}{loc}.json"
            if os.path.exists(os.path.join(path_to_json_corrected, fileName)):
                dateNum, draft, dict_ridge_statistics_corrected, year, loc = load_data.load_data_oneYear(path_to_json_processed=path_to_json_corrected, path_to_json_mooring=path_to_json_mooring,
                                                                                             year=year, loc=loc)
            else:
                dateNum, draft, dict_ridge_statistics_corrected, year, loc = load_data.load_data_oneYear(path_to_json_processed=path_to_json_processed, path_to_json_mooring=path_to_json_mooring,
                                                                                             year=year, loc=loc)
            level_ice_deepest_mode.extend(dict_ridge_statistics_corrected[loc]['level_ice_deepest_mode'])
            mean_keel_draft.extend(dict_ridge_statistics_corrected[loc]['mean_keel_draft'])
    # make a figure with subplot grid (3 columns, 6 rows)
    plt.ion()
    figure_prelim_analysis = plt.figure(layout='constrained', figsize=(8,8)) # 4/5 aspect ratio
    gridspec_prelim_analysis = figure_prelim_analysis.add_gridspec(6,3)
    figure_prelim_analysis.suptitle(f"Preliminary analysis", fontsize=16)

    # figure measured mean ridge keel depth vs level ice deepest mode
    ax_data_ridgeDepth_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[0, 0])
    # curve fitting
    line_x = np.linspace(0, 3, 100)
    line_y = curve_fitting(level_ice_deepest_mode, mean_keel_draft, line_x)
    ax_data_ridgeDepth_LIDM, scatter_data_ridgeDepth_LIDM, line_data_ridgeDepth_LIDM = prelim_plot.plot_scatter_with_line(
        ax_data_ridgeDepth_LIDM, level_ice_deepest_mode, mean_keel_draft, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
        line_x, line_y, {'color':'tab:red'}, 'LI_DM [m]', 'Mean ridge keel depth [m]', xlim=[0, 3], ylim=[5, 9], title="Data")

    # figure some probabilty distribution M/regression?


    # figure simulated mean ridge keel depth vs level ice deepest mode
    ax_sim_ridgeDepth_LIDM = figure_prelim_analysis.add_subplot(gridspec_prelim_analysis[0, 2])
    # curve fitting
    line_x = np.linspace(0, 3, 100)
    



def curve_fitting(data_x, data_y, fitting_x):
    """ curve fitting on the data set data_x, data_y
    """
    matrix_x = np.vstack([data_x, np.ones(len(data_x))]).T
    b = np.linalg.lstsq(matrix_x, data_y, rcond=None)[0]
    fitting_y = b[0]*fitting_x + b[1]
    return fitting_y