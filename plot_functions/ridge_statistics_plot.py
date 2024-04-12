# function for the plots in ridge_statistics_plot.py
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from datetime import datetime as dt



def plot_per_location(dateNum, draft, dateNum_LI, draft_mode, dateNum_rc, draft_rc, dateNum_rc_pd, draft_deepest_ridge, deepest_mode_weekly, R_no, mean_keel_depth, draft_max_weekly, week_to_keep):
    """ Plot the evaluated ridges for one location for one year.
    :param dateNum: numpy array, date number of the ice draft
    :param draft: numpy array, ice draft
    :param dateNum_LI: numpy array, date number of the level ice draft
    :param draft_mode: numpy array, level ice draft
    :param dateNum_rc: numpy array, date number of the ridge crest
    :param draft_rc: numpy array, ridge crest draft
    :param dateNum_rc_pd: numpy array, date number of the ridge crest draft
    :param draft_deepest_ridge: numpy array, deepest ridge draft
    :param deepest_mode_weekly: numpy array, deepest mode weekly
    :param R_no: numpy array, number of ridges
    :param mean_keel_depth: numpy array, mean keel depth
    :param draft_max_weekly: numpy array, weekly deepest ridge draft
    :param week_to_keep: numpy array, week to keep
    :return: figure_ridge_statistics: matplotlib figure, figure with the ridge statistics
    """

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
    axis_deepestRidge_over_iceThickness.scatter(deepest_mode_weekly, draft_deepest_ridge, s=1, c='tab:red', zorder=0, label='expected deepest weekly ridge')
    axis_deepestRidge_over_iceThickness.scatter(deepest_mode_weekly, mean_keel_depth+5, s=1, c='tab:blue', zorder=1, label='expected mean weekly keel depth')
    axis_deepestRidge_over_iceThickness.scatter(deepest_mode_weekly, draft_max_weekly, s=1, c='tab:green', zorder=2, label='weekly deepest ridge')
    axis_deepestRidge_over_iceThickness.legend(prop={'size': 6})


    # number of ridges over mean keel depth
    axis_numberRidges_over_draft = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 2:4])
    axis_numberRidges_over_draft.set_title('number of ridges')
    axis_numberRidges_over_draft.set_xlim(0, 10)
    axis_numberRidges_over_draft.set_xlabel('Draft [m]')
    axis_numberRidges_over_draft.set_ylabel('Number of ridges')
    axis_numberRidges_over_draft.scatter(mean_keel_depth+5, R_no, s=1, c='tab:blue', zorder=0, label='Mean keel depth')
    axis_numberRidges_over_draft.scatter(deepest_mode_weekly, R_no, s=1, c='tab:red', zorder=0, label='deepest mode level ice')
    axis_numberRidges_over_draft.legend(prop={'size': 6})

    # expected deepest keel vs measured deepest keel
    axis_expectedDeepestKeel_over_deepestKeel = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 4:6])
    axis_expectedDeepestKeel_over_deepestKeel.set_title('accuracy of preditciotn')
    axis_expectedDeepestKeel_over_deepestKeel.set_xlim(0, 30)
    axis_expectedDeepestKeel_over_deepestKeel.set_xlabel('Expected deepest keel [m]')
    axis_expectedDeepestKeel_over_deepestKeel.set_ylim(0, 30)
    axis_expectedDeepestKeel_over_deepestKeel.set_ylabel('Measured deepest keel [m]')
    axis_expectedDeepestKeel_over_deepestKeel.plot(np.arange(0, 30, 1), np.arange(0, 30, 1), c='k', linewidth=0.5, zorder=0)
    axis_expectedDeepestKeel_over_deepestKeel.scatter(draft_deepest_ridge, draft_max_weekly, s=1, c='tab:blue', zorder=1)

    return figure_ridge_statistics




def plot_per_year(dict_yearly):
    """ Plot the evaluated ridges for all locations for one year.
    :param dict_yearly: dictionary, dictionary with the yearly ridge statistics
    :return: figure_ridge_statistics: matplotlib figure, figure with the ridge statistics
    """

    colourlist = ['tab:blue', 'tab:orange', 'tab:red', 'tab:cyan', 'tab:olive']
    figure_ridge_statistics = plt.figure(layout='constrained', figsize=(12,9))
    gridspec_ridge_statistics = figure_ridge_statistics.add_gridspec(2,3)
    
    # ice thickness relation to deepest ridge during one week
    axis_deepestRidge_over_iceThickness = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[0,0]) # plt.subplot2grid((2,6), (1,0), colspan=2) # figure_ridge_statistics.add_subplot(2,2,3)
    axis_deepestRidge_over_iceThickness.set_title('expected deepest weekly ridge')
    axis_deepestRidge_over_iceThickness.set_xlim(0, 3)
    axis_deepestRidge_over_iceThickness.set_xlabel('Level ice thickness [m]')
    axis_deepestRidge_over_iceThickness.set_ylim(0, 30)
    axis_deepestRidge_over_iceThickness.set_ylabel('ridge thickness [m]')
    for i, loc in enumerate(dict_yearly.keys()):
        axis_deepestRidge_over_iceThickness.scatter(dict_yearly[loc]['level_ice_deepest_mode'], dict_yearly[loc]['expect_deepest_ridge'], s=1, zorder=0, label= loc, c=colourlist[i])
    axis_deepestRidge_over_iceThickness.legend(prop={'size': 6})
    
    axis_meanRidge_over_iceThickness = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[0,1]) # plt.subplot2grid((2,6), (1,0), colspan=2) # figure_ridge_statistics.add_subplot(2,2,3)
    axis_meanRidge_over_iceThickness.set_title('deepest weekly ridge')
    axis_meanRidge_over_iceThickness.set_xlim(0, 3)
    axis_meanRidge_over_iceThickness.set_xlabel('Level ice thickness [m]')
    axis_meanRidge_over_iceThickness.set_ylim(5, 9)
    axis_meanRidge_over_iceThickness.set_ylabel('ridge thickness [m]')
    for i, loc in enumerate(dict_yearly.keys()):
        axis_meanRidge_over_iceThickness.scatter(dict_yearly[loc]['level_ice_deepest_mode'], dict_yearly[loc]['mean_keel_depth'], s=1, c=colourlist[i], zorder=0, label=loc)
    axis_meanRidge_over_iceThickness.legend(prop={'size': 6})
    
    axis_weeklyDeepestRidge_over_iceThickness = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[0,2]) # plt.subplot2grid((2,6), (1,0), colspan=2) # figure_ridge_statistics.add_subplot(2,2,3)
    axis_weeklyDeepestRidge_over_iceThickness.set_title('deepest weekly ridge')
    axis_weeklyDeepestRidge_over_iceThickness.set_xlim(0, 3)
    axis_weeklyDeepestRidge_over_iceThickness.set_xlabel('Level ice thickness [m]')
    axis_weeklyDeepestRidge_over_iceThickness.set_ylim(0, 30)
    axis_weeklyDeepestRidge_over_iceThickness.set_ylabel('ridge thickness [m]')
    for i, loc in enumerate(dict_yearly.keys()):
        axis_weeklyDeepestRidge_over_iceThickness.scatter(dict_yearly[loc]['level_ice_deepest_mode'], dict_yearly[loc]['draft_weekly_deepest_ridge'], s=1, c=colourlist[i], zorder=0, label=loc)
    axis_weeklyDeepestRidge_over_iceThickness.legend(prop={'size': 6})


    # number of ridges over mean keel depth
    axis_numberRidges_over_draft = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 0])
    axis_numberRidges_over_draft.set_title('number of ridges')
    axis_numberRidges_over_draft.set_xlim(5, 9)
    axis_numberRidges_over_draft.set_xlabel('Draft [m]')
    axis_numberRidges_over_draft.set_ylabel('Number of ridges')
    for i, loc in enumerate(dict_yearly.keys()):
        axis_numberRidges_over_draft.scatter(dict_yearly[loc]['mean_keel_depth'], dict_yearly[loc]['number_ridges'], s=1, c=colourlist[i], zorder=0, label=loc)
    axis_numberRidges_over_draft.legend(prop={'size': 6})

    axis_numberRidges_over_mode = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 1])
    axis_numberRidges_over_mode.set_title('number of ridges')
    axis_numberRidges_over_mode.set_xlim(0, 3)
    axis_numberRidges_over_mode.set_xlabel('Draft [m]')
    axis_numberRidges_over_mode.set_ylabel('Number of ridges')
    for i, loc in enumerate(dict_yearly.keys()):
        axis_numberRidges_over_mode.scatter(dict_yearly[loc]['level_ice_deepest_mode'], dict_yearly[loc]['number_ridges'], s=1, c=colourlist[i], zorder=0, label=loc)
    axis_numberRidges_over_mode.legend(prop={'size': 6})

    # expected deepest keel vs measured deepest keel
    axis_expectedDeepestKeel_over_deepestKeel = figure_ridge_statistics.add_subplot(gridspec_ridge_statistics[1, 2])
    axis_expectedDeepestKeel_over_deepestKeel.set_title('accuracy of preditciotn')
    axis_expectedDeepestKeel_over_deepestKeel.set_xlim(0, 30)
    axis_expectedDeepestKeel_over_deepestKeel.set_xlabel('Expected deepest keel [m]')
    axis_expectedDeepestKeel_over_deepestKeel.set_ylim(0, 30)
    axis_expectedDeepestKeel_over_deepestKeel.set_ylabel('Measured deepest keel [m]')
    axis_expectedDeepestKeel_over_deepestKeel.plot(np.arange(0, 30, 1), np.arange(0, 30, 1), c='k', linewidth=0.5, zorder=0)
    for i, loc in enumerate(dict_yearly.keys()):
        axis_expectedDeepestKeel_over_deepestKeel.scatter(dict_yearly[loc]['expect_deepest_ridge'], dict_yearly[loc]['draft_weekly_deepest_ridge'], s=1, c=colourlist[i], zorder=1, label=loc)
    axis_expectedDeepestKeel_over_deepestKeel.legend(prop={'size': 6})

    return figure_ridge_statistics
