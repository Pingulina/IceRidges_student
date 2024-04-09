# parts of S003_ExtractWeeklyData.m are here

import numpy as np
import os
import sys
import json
import scipy.signal
import scipy.stats
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime as dt

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

def ridge_statistics(poss_mooring_locs=['a', 'b', 'c', 'd'], years=list(range(2004, 2004+1))):
    """Do some statistics; need to be more description
    
    """
    # load the preprocessed data from the weekly_data.json file from the folder weekly_data in Data
    pathName = os.getcwd()
    path_to_json = os.path.join(pathName, 'Data', 'uls_data')

    # preallocate the dict for all years
    dict_yearly = dict()
    dict_yearly['level_ice_deepest_mode'] = [] # LI_DM # level ice estimate
    dict_yearly['level_ice_expect_deepest_mode'] = [] # LI_AM # level ice estimate deepest mode
    dict_yearly['expect_deepest_ridge'] = [] # D - deepest keel estimate
    dict_yearly['number_ridges'] = [] # N - number of ridges
    dict_yearly['mean_keel_depth'] = [] # M - mean keel depth
    dict_yearly['mean_dateNum'] = [] # T - mean date number in the week's subsample
    dict_yearly['week_start'] = [] # WS - start of the week
    dict_yearly['week_end'] = [] # WE - end of the week
    dict_yearly['keel_draft'] = [] # D_all colleciton of all of the keels
    dict_yearly['keel_dateNum'] = [] # T_all collection of all of the times
    dict_yearly['draft_weekly_deepest_ridge'] = [] # Dmax - maximum keel depth in the week
    dict_yearly['year'] = [] # Year of the data
    dict_yearly['location'] = [] # Location of the data
    dict_yearly['peaks_intensity'] = [] # PKSall - intensities of all peaks
    dict_yearly['peaks_location'] = [] # LOCSall - locations of all peaks


    # loop over mooring locations and years, if they are existing in the data, do calculations
    for year in years:
        # # preallocate the dict for all positions in this year
        # dict_yearly[f"{year}"]['level_ice_deepest_mode'] = [] # LI_DM # level ice estimate
        # dict_yearly[f"{year}"]['level_ice_expect_deepest_mode'] = [] # LI_AM # level ice estimate deepest mode
        # dict_yearly[f"{year}"]['expect_deepest_ridge'] = [] # D - deepest keel estimate
        # dict_yearly[f"{year}"]['number_ridges'] = [] # N - number of ridges
        # dict_yearly[f"{year}"]['mean_keel_depth'] = [] # M - mean keel depth
        # dict_yearly[f"{year}"]['mean_dateNum'] = [] # T - mean date number in the week's subsample
        # dict_yearly[f"{year}"]['week_start'] = [] # WS - start of the week
        # dict_yearly[f"{year}"]['week_end'] = [] # WE - end of the week
        # dict_yearly[f"{year}"]['keel_draft'] = [] # D_all colleciton of all of the keels
        # dict_yearly[f"{year}"]['keel_dateNum'] = [] # T_all collection of all of the times
        # dict_yearly[f"{year}"]['draft_weekly_deepest_ridge'] = [] # Dmax - maximum keel depth in the week
        # dict_yearly[f"{year}"]['year'] = [] # Year of the data
        # dict_yearly[f"{year}"]['location'] = [] # Location of the data
        # dict_yearly[f"{year}"]['peaks_intensity'] = [] # PKSall - intensities of all peaks
        # dict_yearly[f"{year}"]['peaks_location'] = [] # LOCSall - locations of all peaks
        for loc in poss_mooring_locs:
            sucess1, dateNum, draft, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_{loc}_draft.json"), loc)
            sucess2, dateNum_rc, draft_rc, _ = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_ridge.json"), loc)
            sucess3, dateNum_LI, draft_LI, draft_mode = j2np.json2numpy(os.path.join(path_to_json, f"mooring_{year}-{year+1}_LI.json"), loc)
            if not (sucess1 and sucess2 and sucess3):
                print(f"Data for {loc} in {year} not found.")
                continue
            dateNum_reshape, draft_reshape = rce.extract_weekly_data_draft(dateNum, draft)
            # preallocate the variables
            week_start = np.zeros((len(dateNum_reshape)))
            week_end = np.zeros((len(dateNum_reshape)))
            # preallocate the dictionaries (store in dict, because the arrays for every week may be of different length, numpy doesn't like this)
            draft_rc_reshape = dict()
            dateNum_rc_reshape = dict()
            week_to_keep = np.zeros((len(dateNum_reshape)), dtype=bool)
            mean_keel_depth = np.zeros((len(dateNum_reshape)))
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
                mean_keel_depth[week_num] = np.mean(draft_rc_reshape[week_num] - constants.min_draft)
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
                Mcdf[f"week_{week_num}"] = cdf.cdf(xxx, mean_keel_depth[week_num]) # np.cumsum(f) / np.sum(f)


                
            print(f"Data for {loc} in {year} extracted weekly.")

            # Estimating the expected deepest ridge
            for week_num in range(len(dateNum_reshape)):
                if not week_to_keep[week_num]:
                    continue
                # find the expected deepest keel depth
                if np.sum(Mcdf[f"week_{week_num}"]) > 0 and not len(draft_rc_reshape[week_num]) == 0:
                    loc, _ = intersections.find_intersections(xxx, (1-1/R_no[week_num]) * np.ones(len(xxx)), xxx, Mcdf[f"week_{week_num}"])
                    draft_deepest_ridge[week_num] = loc + constants.min_draft


            # store the data in the dictionarys (to store as json afterwards)
            dict_yearly['level_ice_deepest_mode'].extend(deepest_mode_weekly)
            dict_yearly['level_ice_expect_deepest_mode'].extend(absolute_mode_weekly)
            dict_yearly['expect_deepest_ridge'].extend(draft_deepest_ridge)
            dict_yearly['number_ridges'].extend(R_no)
            dict_yearly['mean_keel_depth'].extend(mean_keel_depth+5)
            dict_yearly['mean_dateNum'].extend(dateNum_rc_pd)
            dict_yearly['week_start'].extend(week_start)
            dict_yearly['week_end'].extend(week_end)
            dict_yearly['keel_draft'].extend(draft_reshape)
            dict_yearly['keel_dateNum'].extend(dateNum_reshape)
            dict_yearly['draft_weekly_deepest_ridge'].extend(draft_max_weekly)
            dict_yearly['year'].extend([year]*len(dateNum_reshape))
            dict_yearly['location'].extend([loc]*len(dateNum_reshape))
            dict_yearly['peaks_intensity'].extend(intensities_all)
            dict_yearly['peaks_location'].extend(locs_all)

            # dict_yearly[f"{year}"]['level_ice_deepest_mode'].extend(deepest_mode_weekly)
            # dict_yearly[f"{year}"]['level_ice_expect_deepest_mode'].extend(absolute_mode_weekly)
            # dict_yearly[f"{year}"]['expect_deepest_ridge'].extend(draft_deepest_ridge)
            # dict_yearly[f"{year}"]['number_ridges'].extend(R_no)
            # dict_yearly[f"{year}"]['mean_keel_depth'].extend(mean_keel_depth)
            # dict_yearly[f"{year}"]['mean_dateNum'].extend(dateNum_rc_pd)
            # dict_yearly[f"{year}"]['week_start'].extend(week_start)
            # dict_yearly[f"{year}"]['week_end'].extend(week_end)
            # dict_yearly[f"{year}"]['keel_draft'].extend(draft_reshape)
            # dict_yearly[f"{year}"]['keel_dateNum'].extend(dateNum_reshape)
            # dict_yearly[f"{year}"]['draft_weekly_deepest_ridge'].extend(draft_max_weekly)
            # dict_yearly[f"{year}"]['year'].extend([year]*len(dateNum_reshape))
            # dict_yearly[f"{year}"]['location'].extend([loc]*len(dateNum_reshape))
            # dict_yearly[f"{year}"]['peaks_intensity'].extend(intensities_all)
            # dict_yearly[f"{year}"]['peaks_location'].extend(locs_all)
                 
                    
    # plot the data in different plots
    if constants.make_plots:
        figure_ridge_statistics = plt.figure(layout='constrained', figsize=(12,9))
        gridspec_ridge_statistics = figure_ridge_statistics.add_gridspec(2,6)
        # grid_ridge_statistics = gridspec.GridSpec(2,6)
        ###### draft, level ice estimate, all ridges, ridge means
        # 
        axis_draft_LI_ridges = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[0, 0:3]) # plt.subplot2grid((2,6), (0,0), colspan=3) # figure_ridge_statistics.add_subplot(2,2,1)
        axis_draft_LI_ridges.set_title('weekly ice thickness')
        axis_draft_LI_ridges.set_xlim(dateNum[0], dateNum[-1])
        newDayIndex = np.where(dateNum.astype(int)-np.roll(dateNum.astype(int), 1)!=0)
        axis_draft_LI_ridges.set_xticks(dateNum[newDayIndex[0][::60]])
        dateTicks = [str(dt.fromordinal(thisDate))[0:7] for thisDate in dateNum[newDayIndex[0][::60]].astype(int)]
        axis_draft_LI_ridges.set_xticklabels(dateTicks)
        axis_draft_LI_ridges.set_ylabel('draft [m]')


        axis_draft_LI_ridges.plot(dateNum, draft, linewidth=0.1, c='tab:blue', zorder=0, label='draft')
        axis_draft_LI_ridges.plot(dateNum_LI, draft_mode, linewidth=0.6, c='tab:red', zorder=1, label='level ice draft')
        axis_draft_LI_ridges.scatter(dateNum_rc, draft_rc, s=0.5, c='tab:red', zorder=2, label='ridge draft')
        axis_draft_LI_ridges.step(dateNum_rc_pd[week_to_keep], draft_deepest_ridge[week_to_keep], where='mid', c='k', zorder=3, label='draft weekly deepest ridge')
        axis_draft_LI_ridges.step(dateNum_rc_pd[week_to_keep], deepest_mode_weekly[week_to_keep], where='mid', c='k', zorder=4, label='level ice weekly deepest mode')
        axis_draft_LI_ridges.legend(prop={'size': 6})
        
        
        # weekly number of ridges
        axis_weekly_ridges_number = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[0,3:6]) # plt.subplot2grid((2,6), (0,3), colspan=3) # figure_ridge_statistics.add_subplot(2,2,2)
        axis_weekly_ridges_number.set_title('weekly number of ridges')
        axis_weekly_ridges_number.set_xticks(dateNum[newDayIndex[0][::60]])
        axis_weekly_ridges_number.set_xticklabels(dateTicks)
        axis_weekly_ridges_number.set_ylim(0, 400)
        axis_weekly_ridges_number.set_ylabel('number of ridges')

        axis_weekly_ridges_number.step(dateNum_rc_pd[week_to_keep], R_no[week_to_keep], c='k', linewidth=1)

        # ice thickness relation to deepest ridge during one week
        axis_deepestRidge_over_iceThickness = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1,0:2]) # plt.subplot2grid((2,6), (1,0), colspan=2) # figure_ridge_statistics.add_subplot(2,2,3)
        axis_deepestRidge_over_iceThickness.set_title('deepest weekly ridge')
        axis_deepestRidge_over_iceThickness.set_xlim(0, 3)
        axis_deepestRidge_over_iceThickness.set_xlabel('Level ice thickness [m]')
        axis_deepestRidge_over_iceThickness.set_ylim(0, 30)
        axis_deepestRidge_over_iceThickness.set_ylabel('ridge thickness [m]')
        axis_deepestRidge_over_iceThickness.scatter(dict_yearly['level_ice_deepest_mode'], dict_yearly['expect_deepest_ridge'], s=1, c='tab:red', zorder=0, label='expected deepest weekly ridge')
        axis_deepestRidge_over_iceThickness.scatter(dict_yearly['level_ice_deepest_mode'], dict_yearly['mean_keel_depth'], s=1, c='tab:blue', zorder=1, label='expected mean weekly keel depth')
        axis_deepestRidge_over_iceThickness.scatter(dict_yearly['level_ice_deepest_mode'], dict_yearly['draft_weekly_deepest_ridge'], s=1, c='tab:green', zorder=2, label='weekly deepest ridge')
        axis_deepestRidge_over_iceThickness.legend(prop={'size': 6})


        # number of ridges over mean keel depth
        axis_numberRidges_over_deepestRidge = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 2:4])
        axis_numberRidges_over_deepestRidge.set_title('number of ridges')
        axis_numberRidges_over_deepestRidge.set_xlim(5, 10)
        axis_numberRidges_over_deepestRidge.set_xlabel('Mean keel depth [m]')
        axis_numberRidges_over_deepestRidge.set_ylabel('Number of ridges')
        axis_numberRidges_over_deepestRidge.scatter(dict_yearly['mean_keel_depth'], dict_yearly['number_ridges'], s=1, c='tab:blue', zorder=0, label='keel depth')


        # number of ridges over level ice thickness
        axis_numberRidges_over_levelIceThickness = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 4:6])
        axis_numberRidges_over_levelIceThickness.set_title('number of ridges')
        axis_numberRidges_over_levelIceThickness.set_xlim(0, 3)
        axis_numberRidges_over_levelIceThickness.set_xlabel('Level ice thickness [m]')
        axis_numberRidges_over_levelIceThickness.set_ylabel('Number of ridges')
        axis_numberRidges_over_levelIceThickness.scatter(dict_yearly['level_ice_deepest_mode'], dict_yearly['number_ridges'], s=1, c='tab:blue', zorder=0, label='deepest mode level ice')

