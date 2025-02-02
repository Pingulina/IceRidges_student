import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.stats


#### scatter plot functions ####
def initialize_plot_weekly_data_scatter(ax, xData_all, yData_all, xData_thisYear, yData_thisYear, week, xlabel:str, ylabel:str):
    """ do the scatter plot of the weekly data
    """
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    lrs1x = (max(xData_all)-min(xData_all))/40
    lrs1y = (max(yData_all)-min(yData_all))/20
    # all_LIDM = [dict_ridge_statistics[this_year][this_loc]['level_ice_deepest_mode'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    # all_MKD = [dict_ridge_statistics[this_year][this_loc]['mean_keel_draft'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    LI_mode_all = ax.scatter(xData_all, yData_all, color='tab:blue', label='keel depth', zorder=0, alpha=0.5)
    LI_mode_thisYear = ax.scatter(xData_thisYear, yData_thisYear, color='red', label='this year/location', zorder=1, s=4)
    # initialize rectangle to mark the current data point (week)
    CP = mpatches.Rectangle((xData_thisYear[week]-lrs1x/2, yData_thisYear[week]-lrs1y/2), lrs1x, lrs1y, edgecolor='k', facecolor='none')
    # add the patch to the axis
    ax.add_patch(CP)
    
    return ax, LI_mode_all, LI_mode_thisYear, CP

def plot_weekly_data_scatter(ax, LI_mode_all, LI_mode_thisYear, CP, xData_all, yData_all, xData_thisYear, yData_thisYear, week):
    """ do the scatter plot of the weekly data
    """

    lrs1x = (max(xData_all)-min(xData_all))/40
    lrs1y = (max(yData_all)-min(yData_all))/20
    # all_LIDM = [dict_ridge_statistics[this_year][this_loc]['level_ice_deepest_mode'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    # all_MKD = [dict_ridge_statistics[this_year][this_loc]['mean_keel_draft'] for this_year in dict_ridge_statistics.keys() for this_loc in dict_ridge_statistics[this_year].keys()]
    LI_mode_all.set_offsets(np.c_[xData_all, yData_all])
    LI_mode_thisYear.set_offsets(np.c_[xData_thisYear, yData_thisYear])
    # initialize rectangle to mark the current data point (week)
    CP.set_xy([xData_thisYear[week]-lrs1x/2, yData_thisYear[week]-lrs1y/2])
    
    return ax, LI_mode_all, LI_mode_thisYear, CP

def update_plot_weekly_data_scatter(ax, xData_all, yData_all, xData_thisYear, yData_thisYear, week, CP):
    lrs1x = (max(xData_all)-min(xData_all))/40
    lrs1y = (max(yData_all)-min(yData_all))/20
    CP.set_xy([xData_thisYear[week]-lrs1x/2, yData_thisYear[week]-lrs1y/2])

    return ax, CP

def update_plot_weekly_data_scatter_allPoints(ax, xData_all, yData_all, xData_thisYear, yData_thisYear, week, LI_mode_all, LI_mode_thisYear, CP):
    ax, CP = update_plot_weekly_data_scatter(ax, xData_all, yData_all, xData_thisYear, yData_thisYear, week, CP)
    LI_mode_all.set_offsets(np.c_[xData_all, yData_all])
    LI_mode_thisYear.set_offsets(np.c_[xData_thisYear, yData_thisYear])

    return ax, LI_mode_all, LI_mode_thisYear, CP


#### weekly draft data plot functions ####
def initialize_plot_weekly_data_draft(ax, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, week, 
                                      xlabel:str, ylabel:str, ylim, xTickLabels=None, dateTickDistance=1):
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    # make time to np.array
    time = np.array(time)
    dateNum_every_day = time[week][np.where(np.diff(time[week].astype(int)))[0]+1]
    # ax.set_xticks(dateNum_every_day[week*7:(week+1)*7:dateTickDistance])
    ax.set_xticks(dateNum_every_day[:7:dateTickDistance])
    if xTickLabels is not None:
        ax.set_xticklabels(xTickLabels[week*7:(week+1)*7:dateTickDistance])
    
    ULS_draft_signal_thisWeek = ax.plot(time[week], draft[week], color='tab:blue', label='Raw ULS draft signal', zorder=0)
    RidgePeaks_thisWeek = ax.scatter(time_ridge[week], draft_ridge[week], color='red', label='Individual ridge peaks', zorder=1, s=2)
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_thickness_thisWeek = ax.step(keel_dateNum_weekStart[week], draft_LI[week], where='post', color='green', label='Level ice draft estimate', zorder=2)

    return ax, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek

def plot_weekly_data_draft(ax, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, 
                           dateNum_every_day, week, xTickLabels, ylim, dateTickDistance=1):
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_xticks(dateNum_every_day[week*7:(week+1)*7:dateTickDistance])
    ax.set_xticklabels(xTickLabels[week*7:(week+1)*7:dateTickDistance])
    ax.set_xlim(dateNum_every_day[week*7], dateNum_every_day[(week+1)*7])
    
    ULS_draft_signal_thisWeek[0].set_xdata(time[week])
    ULS_draft_signal_thisWeek[0].set_ydata(draft[week])
    RidgePeaks_thisWeek.set_offsets(np.c_[time_ridge[week], draft_ridge[week]])
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_thickness_thisWeek[0].set_xdata(keel_dateNum_weekStart[week])
    LI_thickness_thisWeek[0].set_ydata(draft_LI[week])

    return ax, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek

def update_plot_weekly_data_draft(ax, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek, time, draft, time_ridge, draft_ridge, 
                                  time_LI, draft_LI, dateNum_every_day, week, xTickLabels):
    ax.set_xticks(dateNum_every_day[week*7:(week+1)*7])
    ax.set_xticklabels(xTickLabels[week*7:(week+1)*7])
    ax.set_xlim(dateNum_every_day[week*7], dateNum_every_day[(week+1)*7])

    ULS_draft_signal_thisWeek[0].set_xdata(time[week])
    ULS_draft_signal_thisWeek[0].set_ydata(draft[week])

    RidgePeaks_thisWeek.set_offsets(np.c_[time_ridge[week], draft_ridge[week]])

    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_thickness_thisWeek[0].set_xdata(keel_dateNum_weekStart[week])
    LI_thickness_thisWeek[0].set_ydata(draft_LI[week])

    return ax, ULS_draft_signal_thisWeek, RidgePeaks_thisWeek, LI_thickness_thisWeek


#### draft data plot functions ####
def initialize_plot_data_draft(ax, time, draft, time_ridge, draft_ridge, time_LI, draft_LI, week_starts, week_ends, week, every_nth_xTick, 
                               xlabel:str, ylabel:str, ylim, xTickLabels=None, legend=True):
    ax.set_ylim(ylim[0], ylim[1])
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    # the x data is dateNum format, but the x labels should be the date in the format 'YYYY-MM-DD', every 50th day is labeled. DateNum has 24*3600 entries per day
    dateNum_every_day = time[np.where(np.diff(time.astype(int)))[0]+1]
    ax.set_xticks(dateNum_every_day[::every_nth_xTick])
    if xTickLabels is not None:
        ax.set_xticklabels(xTickLabels[::every_nth_xTick])


    keel_draft_flat = [x for xs in draft_ridge for x in xs]
    keel_dateNum_flat = [x for xs in time_ridge for x in xs]
    patch_current_week_ice_data = ax.fill_between([week_starts[week], week_ends[week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)
    ULS_draft_signal = ax.plot(time, draft, color='tab:blue', label='Raw ULS draft signal', zorder=1)
    RidgePeaks = ax.scatter(keel_dateNum_flat, keel_draft_flat, color='red', label='Individual ridge peaks', s=0.75, zorder=2)
    # take the first element of each list in keel_dateNum and write it in keel_dateNum_weekStart
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_thickness = ax.step(keel_dateNum_weekStart, draft_LI, where='post', color='black', label='Level ice draft estimate', zorder=3)

    if legend:
        ax.legend(loc='upper left')

    return ax, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness

def plot_data_draft(ax, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness, time, draft, time_ridge, draft_ridge,
                                       time_LI, draft_LI, week_starts, week_ends, week, every_nth_xTick, xTickLabels, ylim):
    ax.set_ylim(ylim[0], ylim[1])
    # the x data is dateNum format, but the x labels should be the date in the format 'YYYY-MM-DD', every 50th day is labeled. DateNum has 24*3600 entries per day
    dateNum_every_day = time[np.where(np.diff(time.astype(int)))[0]+1]
    ax.set_xticks(dateNum_every_day[::every_nth_xTick])
    ax.set_xticklabels(xTickLabels[::every_nth_xTick])


    keel_draft_flat = [x for xs in draft_ridge for x in xs]
    keel_dateNum_flat = [x for xs in time_ridge for x in xs]
    patch_current_week_ice_data.remove()
    patch_current_week_ice_data = ax.fill_between([week_starts[week], week_ends[week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)
    ULS_draft_signal[0].set_xdata(time)
    ULS_draft_signal[0].set_ydata(draft)
    RidgePeaks.set_offsets(np.c_[keel_dateNum_flat, keel_draft_flat])
    # take the first element of each list in keel_dateNum and write it in keel_dateNum_weekStart
    keel_dateNum_weekStart = [date[0] for date in time_LI]
    LI_thickness[0].set_xdata(keel_dateNum_weekStart)
    LI_thickness[0].set_ydata(draft_LI)

    return ax, patch_current_week_ice_data, ULS_draft_signal, RidgePeaks, LI_thickness

def update_plot_data_draft(ax, patch_current_week_ice_data, draft, week_starts, week_ends, week):
    patch_current_week_ice_data.remove()
    patch_current_week_ice_data = ax.fill_between([week_starts[week], week_ends[week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)

    return ax, patch_current_week_ice_data


#### distribution plot functions ####
def initialize_plot_needName(ax, time, draft, week_starts, week_ends, week, LI_deepestMode_expect, LI_deepestMode, peaks_location, peaks_intensity):
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 6)
    ax.set_xlabel('Draft [m]')
    draft_subset = draft[np.intersect1d(np.where(draft > 0), np.intersect1d(np.where(time > week_starts[week]), np.where(time < week_ends[week])))]
    # bw_sigma = np.std(draft_subset)
    # bw_n = len(draft_subset)
    # bw_h = 1.06*bw_sigma*bw_n**(-1/5)
    kde = scipy.stats.gaussian_kde(draft_subset)
    xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
    f = kde(xi)
    # ax_kernel_estimate.plot(xi, f, color='tab:blue', label='Kernel estimate', zorder=1)
    # plot level ice deepest mode
    DM_line = ax.plot([0, 0], [0, 6], color='tab:blue', label='deepest mode LI', zorder=1)
    AM_line = ax.plot([0, 0], [0, 6], color='red', label='average mode LI', ls='--', zorder=2)
    kernel_estimate_line = ax.plot(xi, f, color='tab:red', label='Kernel estimate', zorder=3)
    PS_line = ax.scatter(0, 0, color='k', zorder=3, label='peak signal', s=12)
    # histogram_line = ax_kernel_estimate.hist(draft_subset, bins=20, color='k', alpha=0.5, zorder=0, density=True)
    number_of_bins = int((max(draft_subset) - min(draft_subset))/0.05)
    histogram_numpy = np.histogram(draft_subset, bins=number_of_bins, density=True)
    histogram_line = ax.bar(histogram_numpy[1][:-1], histogram_numpy[0], align='edge', color='k', alpha=0.5, zorder=0, width=(max(draft_subset)-min(draft_subset))/number_of_bins)
    # ax_kernel_estimate.legend()

    DM_line[0].set_xdata(LI_deepestMode_expect[week])
    AM_line[0].set_xdata(LI_deepestMode[week])
    kernel_estimate_line[0].set_xdata(xi)
    kernel_estimate_line[0].set_ydata(f)
    PS_line.set_offsets([[loc, pks] for loc, pks in zip(peaks_location[week], peaks_intensity[week])])

    return ax, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line

def plot_needName(ax, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line, time, draft, week_starts, week_ends, week, LI_deepestMode_expect, 
                  LI_deepestMode, peaks_location, peaks_intensity):
    draft_subset = draft[np.intersect1d(np.where(draft > 0), np.intersect1d(np.where(time > week_starts[week]), np.where(time < week_ends[week])))]
    # bw_sigma = np.std(draft_subset)
    # bw_n = len(draft_subset)
    # bw_h = 1.06*bw_sigma*bw_n**(-1/5)
    kde = scipy.stats.gaussian_kde(draft_subset)
    xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
    f = kde(xi)
    # ax_kernel_estimate.plot(xi, f, color='tab:blue', label='Kernel estimate', zorder=1)
    # plot level ice deepest mode
    # histogram_line = ax_kernel_estimate.hist(draft_subset, bins=20, color='k', alpha=0.5, zorder=0, density=True)
    number_of_bins = int((max(draft_subset) - min(draft_subset))/0.05)
    histogram_numpy = np.histogram(draft_subset, bins=number_of_bins, density=True)
    histogram_line.remove()
    histogram_line = ax.bar(histogram_numpy[1][:-1], histogram_numpy[0], align='edge', color='k', alpha=0.5, zorder=0, width=(max(draft_subset)-min(draft_subset))/number_of_bins)
    # ax_kernel_estimate.legend()

    DM_line[0].set_xdata(LI_deepestMode_expect[week])
    AM_line[0].set_xdata(LI_deepestMode[week])
    kernel_estimate_line[0].set_xdata(xi)
    kernel_estimate_line[0].set_ydata(f)
    PS_line.set_offsets([[loc, pks] for loc, pks in zip(peaks_location[week], peaks_intensity[week])])

    return ax, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line


def update_plot_needName(ax, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line, time, draft, week_starts, week_ends, week, 
                         LI_deepestMode_expect, LI_deepestMode, peaks_location, peaks_intensity):
    draft_subset = draft[np.intersect1d(np.where(draft > 0), np.intersect1d(np.where(time > week_starts[week]), np.where(time < week_ends[week])))]
    kde = scipy.stats.gaussian_kde(draft_subset)
    xi = np.linspace(draft_subset.min(), draft_subset.max(), 100)
    f = kde(xi)
    number_of_bins = int((max(draft_subset) - min(draft_subset))/0.05)
    histogram_line.remove()
    histogram_numpy = np.histogram(draft_subset, bins=number_of_bins, density=True)
    histogram_line = ax.bar(histogram_numpy[1][:-1], histogram_numpy[0], align='edge', color='k', alpha=0.5, zorder=0, width=(max(draft_subset)-min(draft_subset))/number_of_bins)
    # histogram_line = ax_kernel_estimate.hist(draft_subset, bins=20, color='k', alpha=0.5, zorder=0, density=True)

    DM_line[0].set_xdata(LI_deepestMode_expect[week])
    AM_line[0].set_xdata(LI_deepestMode[week])
    kernel_estimate_line[0].set_xdata(xi)
    kernel_estimate_line[0].set_ydata(f)
    PS_line.set_offsets([[loc, pks] for loc, pks in zip(peaks_location[week], peaks_intensity[week])])
    return ax, DM_line, AM_line, kernel_estimate_line, PS_line, histogram_line


#### spectrum plot functions ####
def initialize_plot_spectrum(ax, draft, time_mean, LI_deepestMode, LI_deepestMode_expect, week_starts, week_ends, week):
    # ax.pcolormesh(X, Y, HHi_plot.transpose(), shading='nearest')
    ax.set_ylim([0, 4])
    ax.set_xlabel('Time')
    ax.set_ylabel('Draft')
    ax.set_xlim([time_mean[0]+3.5, time_mean[-1]-10.5])

    colorMesh = ax.pcolormesh(np.arange(len(time_mean)), np.arange(len(LI_deepestMode)), np.zeros((len(time_mean), len(LI_deepestMode)), dtype=float), shading='nearest', zorder=0)
    patch_current_week_ice_data = ax.fill_between([week_starts[week], week_ends[week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=1)
    scatter_DM = ax.scatter(time_mean, LI_deepestMode, c='r', s=10, marker='o', zorder=2) # scatter shape: circles
    scatter_AM = ax.scatter(time_mean, LI_deepestMode_expect, c='b', s=10, marker='^', zorder=3) # scatter shape: triangles
    lrs1x = (ax.get_xlim()[1]-ax.get_xlim()[0])/20
    lrs1y = (ax.get_ylim()[1]-ax.get_ylim()[0])/20
    CP = mpatches.Rectangle((time_mean[week]-lrs1x/2, LI_deepestMode[week]-lrs1y/2), lrs1x, lrs1y, edgecolor='r', facecolor='none', zorder=4)
    # add the patch to the axis
    ax.add_patch(CP)

    return ax, colorMesh, patch_current_week_ice_data, scatter_DM, scatter_AM, CP


def plot_spectrum(ax, colorMesh, patch_current_week_ice_data, scatter_DM, scatter_AM, CP, X, Y, HHi_plot, draft, time_mean, time_LI, LI_deepestMode, 
                  LI_deepestMode_expect, week_starts, week_ends, week):
    ax.set_ylim([0, 4])
    ax.set_xlim([time_LI[0]+3.5, time_LI[-1]-10.5])

    colorMesh.remove()
    colorMesh = ax.pcolormesh(X, Y, HHi_plot.transpose(), shading='nearest')
    patch_current_week_ice_data.remove()
    patch_current_week_ice_data = ax.fill_between([week_starts[week], week_ends[week]], 0, max(draft), color='lightblue', label='Current week ice data', zorder=0)
    scatter_DM.set_offsets(np.c_[time_mean, LI_deepestMode])
    scatter_AM.set_offsets(np.c_[time_mean, LI_deepestMode_expect])
    lrs1x = (ax.get_xlim()[1]-ax.get_xlim()[0])/20
    lrs1y = (ax.get_ylim()[1]-ax.get_ylim()[0])/20
    CP.set_xy([time_mean[week]-lrs1x/2, LI_deepestMode[week]-lrs1y/2])

    return ax, colorMesh, patch_current_week_ice_data, scatter_DM, scatter_AM, CP


def update_plot_spectrum(ax, CP, time_mean, LI_deepestMode, week):
    lrs1x = (ax.get_xlim()[1]-ax.get_xlim()[0])/20
    lrs1y = (ax.get_ylim()[1]-ax.get_ylim()[0])/20
    CP.set_xy([time_mean[week]-lrs1x/2, LI_deepestMode[week]-lrs1y/2])

    return ax, CP