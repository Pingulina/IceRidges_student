### figure uls data, ridges, level ice whole year
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
ax_pres, patch_current_week_ice_data_pres, ULS_draft_signal_pres, RidgePeaks_pres, LI_thickness_pres = data_analysis_plot.initialize_plot_data_draft(
    ax_pres, dateNum, draft, dict_ridge_statistics[loc]['keel_dateNum_ridge'], dict_ridge_statistics[loc]['keel_draft_ridge'], 
    dict_ridge_statistics[loc]['keel_dateNum'], dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['week_start'], 
    dict_ridge_statistics[loc]['week_end'], week, every_nth, 'Date', 'Draft [m]', [0, 30], xTickLabels=xTickLabels)

patch_current_week_ice_data_pres.remove()
ax_pres.get_legend().remove()
ax_pres.legend(loc='upper left')
ax_pres.get_xaxis().get_label().set_size(20)
ax_pres.get_yaxis().get_label().set_size(20)


### scatter LI mean keel draft
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
ax_pres, LI_mode_all_pres, LI_mode_thisYear_pres, CP1_pres = data_analysis_plot.initialize_plot_weekly_data_scatter(
    ax_pres, all_LIDM, all_MKD, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['mean_keel_draft'], 
    week, 'Level ice deepest mode [m]', 'Mean keel draft [m]')

ax_pres.set_xlabel('Level ice [m]', fontsize=40)
ax_pres.set_ylabel('Ridge draft [m]', fontsize=40)
ax_pres.get_xaxis().get_label().set_size(40)
ax_pres.get_yaxis().get_label().set_size(40)
ax_pres.set_aspect('equal','box')
CP1_pres.remove()

LI_mode_thisYear_pres.set_sizes([20])
LI_mode_all_pres.set_sizes([150])


### number ridges LI
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
ax_pres, number_of_ridges_all_pres, number_of_ridges_thisYear_pres, CP4_pres = data_analysis_plot.initialize_plot_weekly_data_scatter(
    ax_pres, all_LIDM, all_number_of_ridges, dict_ridge_statistics[loc]['level_ice_deepest_mode'], dict_ridge_statistics[loc]['number_ridges'], 
    week, 'Level ice deepest mode [m]', 'Number of ridges')
ax_pres.set_xlabel('Level ice [m]', fontsize=40)
ax_pres.set_ylabel('Number of ridges', fontsize=40)
CP4_pres.remove()

number_of_ridges_thisYear_pres.set_sizes([20])
number_of_ridges_all_pres.set_sizes([150])



#### spectrum
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
ax_pres
ax_pres, colorMesh_specto_pres, thisWeek_patch_specto_pres, scatter_pres, scatter_AM_pres, CP5_pres = data_analysis_plot.initialize_plot_spectrum(
    ax_pres, draft, dict_ridge_statistics_year_all[dummy_year][dummy_loc]['mean_dateNum'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_deepest_mode'], 
    dict_ridge_statistics_year_all[dummy_year][dummy_loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_start'], 
    dict_ridge_statistics_year_all[dummy_year][dummy_loc]['week_end'], dummy_week)
ax_pres, colorMesh_specto_pres, thisWeek_patch_specto_pres, scatter_pres, scatter_AM_pres, CP5_pres = data_analysis_plot.plot_spectrum(
    ax_pres, colorMesh_specto_pres, thisWeek_patch_specto_pres, scatter_pres, scatter_AM_pres, CP5_pres,
    X, Y, HHi_plot, draft, dict_ridge_statistics[loc]['mean_dateNum'], dateNum_LI, dict_ridge_statistics[loc]['level_ice_deepest_mode'], 
    dict_ridge_statistics[loc]['level_ice_expect_deepest_mode'], dict_ridge_statistics[loc]['week_start'], dict_ridge_statistics[loc]['week_end'], week)


ax_pres.get_xaxis().get_label().set_size(20)
ax_pres.get_yaxis().get_label().set_size(20)
scatter_AM_pres.set_sizes([40])
scatter_AM_pres.set_color('k')
scatter_pres.set_sizes([40])




########## in prelim_analysis_simulation.py
##### probdist mean keel depth
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
regression_ridgeDepth = np.divide(mean_keel_draft, fitting_y(level_ice_deepest_mode, b))
line_x = np.arange(0.79, 1.2, 0.02)
ax_pres, hist_ridgeDepth_probDist_pres, line_ridgeDepth_probDist_pres, ridgeDepth_probDist_pres = prelim_plot.plot_histogram_with_line(
    ax_pres, regression_ridgeDepth, {'color':'tab:blue', 'bins':20}, line_x, {'color':'tab:red'}, 
    'normalized mean keel depth', 'Probabitly distribution', xlim=[0.8, 1.2])
ax_pres.get_xaxis().get_label().set_size(20)
ax_pres.get_yaxis().get_label().set_size(20)


#### probDist number ridges
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
regression_ridgeNumber = np.divide(number_of_ridges, 38.78 * (mean_keel_draft-constants.min_draft) ** 2.047)
line_x = np.arange(0, 3, 0.01)
ax_pres, hist_ridgeNumber_probDist, line_ridgeNumber_probDist, ridgeNumber_probDist = prelim_plot.plot_histogram_with_line(
    ax_pres, regression_ridgeNumber, {'color':'tab:blue', 'bins':20}, line_x, {'color':'tab:red', 'distribution':'nakagami'}, 
    'normalized number of ridges', 'Probabitly distribution', xlim=[0, 3])
ax_pres.get_xaxis().get_label().set_size(20)
ax_pres.get_yaxis().get_label().set_size(20)


#### keel depth data vs sim
fig_pres = plt.figure()
ax_pres = fig_pres.add_subplot(111)
line_x = np.arange(0, 40, 1)
line_y = np.arange(0, 40, 1)
# equal axis
ax_pres.set_aspect('equal', adjustable='box')
ax_pres, scatter_weekly_deepest_keel_sim_data_pres, line_weekly_deepest_keel_sim_data_pres = prelim_plot.plot_scatter_with_line(
    ax_pres, draft_weekly_deepest_ridge, keel_draft_ridge_toKeep_max_sim, {'color':'tab:blue', 'marker':'o', 's':6, 'alpha':0.5}, 
    line_x, line_y, {'color':'tab:red'}, 'Data[m]', 'Simulation [m]', xlim=[5, 40], ylim=[5, 40], title="Weekly deepest keel")

ax_pres.get_xaxis().get_label().set_size(20)
ax_pres.get_yaxis().get_label().set_size(20)
scatter_weekly_deepest_keel_sim_data_pres.set_sizes([20])


