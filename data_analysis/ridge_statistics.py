# parts of S003_ExtractWeeklyData.m are here

import numpy as np
import os
import sys
import scipy.signal
import scipy.stats
from copy import deepcopy
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
# import the date_time_stuff module from the helper_functions directory
rce = import_module('ridge_compute_extract', 'data_handling')
j2np = import_module('json2numpy', 'data_handling')
intersections = import_module('intersections', 'helper_functions')
constants = import_module('constants', 'helper_functions')
cdf = import_module('cdf', 'helper_functions')
ridge_statistics_plot = import_module('ridge_statistics_plot', 'plot_functions')
dict2json = import_module('dict2json', 'data_handling')

def ridge_statistics(poss_mooring_locs=['a', 'b', 'c', 'd'], years=[2004], saveAsJson=False):
    """Do some statistics; need to be more description
    
    """
    # years = list(range(years[0], years[1]+1))
    # load the preprocessed data from the weekly_data.json file from the folder weekly_data in Data
    pathName = os.getcwd()
    path_to_json = os.path.join(pathName, 'Data', 'uls_data')

    # preallocate the dict for all years
    # dict_ridge_statistics = dict()


    # loop over mooring locations and years, if they are existing in the data, do calculations
    for year in years:
        dict_yearly = dict()

        for loc in poss_mooring_locs:
            sucess1, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)
            sucess2, dateNum_rc, draft_rc, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_ridge.json"), loc)
            sucess3, dateNum_LI, draft_LI, draft_mode = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_LI.json"), loc)
            if not (sucess1 and sucess2 and sucess3):
                print(f"Data for {loc} in {year} not found.")
                continue
            dateNum_reshape, draft_reshape = rce.extract_weekly_data_draft(dateNum, draft)

            # preallocate the dictionary for the location
            dict_yearly[loc] = dict()
            dict_yearly[loc]['level_ice_deepest_mode'] = [] # LI_DM # level ice estimate
            dict_yearly[loc]['level_ice_expect_deepest_mode'] = [] # LI_AM # level ice estimate deepest mode
            dict_yearly[loc]['expect_deepest_ridge'] = [] # D - deepest keel estimate
            dict_yearly[loc]['number_ridges'] = [] # N - number of ridges
            dict_yearly[loc]['mean_keel_draft'] = [] # M - mean keel depth
            dict_yearly[loc]['mean_dateNum'] = [] # T - mean date number in the week's subsample
            dict_yearly[loc]['week_start'] = [] # WS - start of the week
            dict_yearly[loc]['week_end'] = [] # WE - end of the week
            dict_yearly[loc]['keel_draft'] = [] #  colleciton of all of the keels
            dict_yearly[loc]['keel_dateNum'] = [] #  collection of all of the times
            dict_yearly[loc]['keel_draft_ridge'] = [] # D_all - keel depth of the ridges
            dict_yearly[loc]['keel_dateNum_ridge'] = [] # T_all - time of the ridges
            dict_yearly[loc]['draft_weekly_deepest_ridge'] = [] # Dmax - maximum keel depth in the week
            dict_yearly[loc]['year'] = [] # Year of the data
            dict_yearly[loc]['location'] = [] # Location of the data
            dict_yearly[loc]['peaks_intensity'] = [] # PKSall - intensities of all peaks
            dict_yearly[loc]['peaks_location'] = [] # LOCSall - locations of all peaks
            dict_yearly[loc]['week_to_keep'] = [] # flag to keep the week
            
            
            # preallocate the variables
            week_start = np.zeros((len(dateNum_reshape)))
            week_end = np.zeros((len(dateNum_reshape)))
            # preallocate the dictionaries (store in dict, because the arrays for every week may be of different length, numpy doesn't like this)
            draft_rc_reshape = dict()
            dateNum_rc_reshape = dict()
            week_to_keep = np.zeros((len(dateNum_reshape)), dtype=bool)
            mean_keel_draft = np.zeros((len(dateNum_reshape)))
            dateNum_rc_pd = np.zeros((len(dateNum_reshape)))
            draft_max_weekly = np.zeros((len(dateNum_reshape)))
            deepest_mode_weekly = np.zeros((len(dateNum_reshape)))
            R_no = np.zeros((len(dateNum_reshape)))

            intensities_all = dict()
            locs_all = dict()
            absolute_mode_weekly = np.zeros((len(dateNum_reshape)))
            Mcdf = dict()

            # preallocating an xxx vecor to be used for expected maximum ridge calculation
            xxx = np.arange(0, 30, 0.01)

            draft_deepest_ridge = np.zeros((len(dateNum_reshape)))



            for week_num in range(len(dateNum_reshape)):
                dateNum_rc_reshape, draft_rc_reshape, week_start, week_end = rce.extract_weekly_data_draft_ridge(dateNum_rc, draft_rc, dateNum_reshape, draft_reshape,
                                        dateNum_rc_reshape, draft_rc_reshape, week_start, week_end, week_num)
                
                # number of ridges in this week
                R_no[week_num] = np.array([len(draft_rc_reshape[week_num])])
                
                # find a subset of the raw ULS draft measurement
                draft_subset = draft[np.intersect1d(
                    np.intersect1d(np.where(draft < 3), np.where(draft >= 0)), 
                    np.intersect1d(np.where(dateNum > week_start[week_num]), np.where(dateNum < week_end[week_num]))
                    )]
                # if there are too few ridge data points, skip the week
                if len(dateNum_rc_reshape[week_num]) <= 5 or draft_subset.size == 0:
                    continue

                week_to_keep[week_num] = True

                # pd_ridges = exponential_fit() # fit exponential distribution to the ridges
                dateNum_rc_pd[week_num] = np.mean(dateNum_rc_reshape[week_num])
                mean_keel_draft[week_num] = np.mean(draft_rc_reshape[week_num] - constants.min_draft)
                draft_max_weekly[week_num] = np.max(draft_rc_reshape[week_num]) # deepest weekly draft


                # kernel estimate of the draft PDF
                kde = scipy.stats.gaussian_kde(draft_subset)
                xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
                f = kde(xi)

                # indices of all modes
                locs_idx, _ = scipy.signal.find_peaks(f)
                # locations and intensities of all peaks
                locs = xi[locs_idx]
                intensities = f[locs_idx]

                # find the mode with the deepest draft
                if not len(locs) == 0:
                    mode_loc_idx = np.argmax(locs)
                    mode_idx = np.max(np.where(intensities > 0.25))
                    # mode_idx = np.argmax(intensities)
                    mode = locs[mode_idx]
                    deepest_mode_weekly[week_num] = mode
                else:
                    deepest_mode_weekly[week_num] = 0
                    week_to_keep[week_num] = False

                intensities_all[f"week_{week_num}"] = deepcopy(intensities)
                locs_all[f"week_{week_num}"] = deepcopy(locs)

                # find the intensity and location of the absolute mode
                if len(locs) > 0:
                    mode_idx = np.argmax(intensities)
                    locs = locs[mode_idx]
                    intensities = intensities[mode_idx]
                else:
                    locs = 0
                    intensities = 0

                absolute_mode_weekly[week_num] = locs

                # cdf of the estimated exponential distribution, used later fo estimating the expected deepest keel
                Mcdf[f"week_{week_num}"] = cdf.cdf(xxx, mean_keel_draft[week_num]) # np.cumsum(f) / np.sum(f)


                
            print(f"Data for {loc} in {year} extracted weekly.")

            # Estimating the expected deepest ridge
            for week_num in range(len(dateNum_reshape)):
                if not week_to_keep[week_num]:
                    continue
                # find the expected deepest keel depth
                if np.sum(Mcdf[f"week_{week_num}"]) > 0 and not len(draft_rc_reshape[week_num]) == 0:
                    loc_inter, _ = intersections.find_intersections(xxx, (1-1/R_no[week_num]) * np.ones(len(xxx)), xxx, Mcdf[f"week_{week_num}"])
                    draft_deepest_ridge[week_num] = loc_inter + constants.min_draft


            # store the data in the dictionarys (to store as json afterwards)
            dict_yearly[loc]['level_ice_deepest_mode'].extend(deepcopy(deepest_mode_weekly))
            dict_yearly[loc]['level_ice_expect_deepest_mode'].extend(deepcopy(absolute_mode_weekly))
            dict_yearly[loc]['expect_deepest_ridge'].extend(deepcopy(draft_deepest_ridge))
            dict_yearly[loc]['number_ridges'].extend(deepcopy(R_no))
            dict_yearly[loc]['mean_keel_draft'].extend(deepcopy(mean_keel_draft+constants.min_draft))
            dict_yearly[loc]['mean_dateNum'].extend(deepcopy(dateNum_rc_pd))
            dict_yearly[loc]['week_start'].extend(deepcopy(week_start))
            dict_yearly[loc]['week_end'].extend(deepcopy(week_end))
            dict_yearly[loc]['keel_draft'].extend(deepcopy(draft_reshape))
            dict_yearly[loc]['keel_dateNum'].extend(deepcopy(dateNum_reshape))
            dict_yearly[loc]['keel_draft_ridge'].extend(deepcopy([value for key, value in draft_rc_reshape.items()])) # this is a dict with entries for every week, make a list instead
            dict_yearly[loc]['keel_dateNum_ridge'].extend(deepcopy([value for key, value in dateNum_rc_reshape.items()]))
            dict_yearly[loc]['draft_weekly_deepest_ridge'].extend(deepcopy(draft_max_weekly))
            dict_yearly[loc]['year'].extend(deepcopy([year]*len(dateNum_reshape)))
            dict_yearly[loc]['location'].extend(deepcopy([loc]*len(dateNum_reshape)))
            dict_yearly[loc]['peaks_intensity'].extend(deepcopy([value for key, value in intensities_all.items()]))
            dict_yearly[loc]['peaks_location'].extend(deepcopy([value for key, value in locs_all.items()]))
            dict_yearly[loc]['week_to_keep'].extend(deepcopy(week_to_keep))
                    
            # plot the data in different plots (one figure) (one figure per location and year)
            if constants.make_plots:
                figure_ridge_statistics = ridge_statistics_plot.plot_per_location(dateNum, draft, dateNum_LI, draft_mode, dateNum_rc, draft_rc, dateNum_rc_pd, 
                                                                                  draft_deepest_ridge, deepest_mode_weekly, R_no, mean_keel_draft, draft_max_weekly, 
                                                                                  week_to_keep)
                
                # save the plot
                pathName_thisPlot = os.path.join(constants.pathName_plots, 'ridge_statistics')
                if not os.path.exists(pathName_thisPlot):
                    os.makedirs(pathName_thisPlot)
                figure_ridge_statistics.savefig(os.path.join(pathName_thisPlot, f"ridge_statistics_{year}{loc}.png"))
                # close the plot
                plt.close(figure_ridge_statistics)


        # # store dict_yearly to dict_ridge_statistics
        # dict_ridge_statistics[f"{year}"] = deepcopy(dict_yearly) # deepcopy, because the dict_yearly is overwritten in the next iteration

        if saveAsJson:
            # save the data in a json file
            pathName_thisData = os.path.join(constants.pathName_dataResults, 'ridge_statistics')
            if not os.path.exists(pathName_thisData):
                os.makedirs(pathName_thisData)
            for loc in dict_yearly.keys():
                dict2json.dict2json(dict_yearly[loc], os.path.join(pathName_thisData, f"ridge_statistics_{year}{loc}.json"))
            
        # plot the data of all mooring locations from this year
        if constants.make_plots:
            figure_ridge_statistics = ridge_statistics_plot.plot_per_year(dict_yearly)

            # save the plot
            pathName_thisPlot = os.path.join(constants.pathName_plots, 'ridge_statistics')
            if not os.path.exists(pathName_thisPlot):
                os.makedirs(pathName_thisPlot)
            figure_ridge_statistics.savefig(os.path.join(pathName_thisPlot, f"ridge_statistics_{year}_all.png"))
            # close the plot
            plt.close(figure_ridge_statistics)

        if constants.make_plots:
            print(f"Data for year {year} extracted and plots saved at {pathName_thisPlot}.")
        else:
            print(f"Data for year {year} extracted.")

    return None
    # return dict_ridge_statistics

    