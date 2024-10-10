# this is the main function for the ice ridge code
import os


import initialization_preparation.initialize_python as init_py


def main():
    # init_py.initialize_python()
    # import files must be behind the initialization of the python environment, otherwise it doesn't compile if the python packages aren't installed yet
    import json

    import initialization_preparation.data2json as d2j
    import initialization_preparation.extract_ridge_LI_data as ewd
    import initialization_preparation.data2dict as d2d
    import data_analysis.ridge_statistics as rs
    import data_analysis.weekly_visual_analysis as wva
    import data_handling.dict2json as dict2json
    import data_analysis.weekly_manual_correction as wmc
    import data_analysis.preliminary_analysis_simulation as pas
    import data_analysis.level_ice_statistics as lis
    import data_analysis.level_ice_statistics_multiYear as lisMY
    import data_analysis.mode_threshold_analysis as mta
    import simulation_functions.simulation_deepest_ridge as sdr
    import simulation_functions.simulation_all_ridges as sar
    # d2j.example() # store the .dat files as .json files for the mooring data

    # rs.ridge_statistics()
    # d2d.example()

    ### uncomment the following line to run the extract_ridge_LI_data.py file
    # ewd.extract_ridge_LI_data(overwrite=True)

    ### uncomment the following line to run the ridge_statistics.py file
    # rs.ridge_statistics(years=[2004, 2005, 2006], poss_mooring_locs=['a','b','c','d'], saveAsJson=True) # , 2005, 2006

    ### uncomment the following line to run the weekly_visual_analysis.py file
    # wva.weekly_visual_analysis()

    ### uncomment the following line to run the weekly_manual_correction.py file
    # wmc.weekly_manual_correction()

    ### uncomment the following line to run the preliminary_analysis_simulation.py file
    pas.prelim_analysis_simulation([2004, 2006], ['a', 'b', 'c', 'd'])

    ### uncomment the following line to run the level_ice_statistics.py file
    # lis.level_ice_statistics(year=2004, loc='a')

    ### uncomment the following line to run the level_ice_statistics_multiYear.py file
    # lisMY.level_ice_statistics_multiYear()

    ### uncomment the following line to run the mode_threshold_analysis.py file
    # mta.mode_threshold_analysis()

    ### uncomment the following line to run the simulation_deepest_ridge.py file
    # sdr.simulate_deepest_ridge()

    ### uncomment the following line to run the simulation_all_ridges.py file
    # sar.simulate_all_ridges()

    return None

if __name__ == "__main__":
    print("main.py is being run directly")
    main()
    print("main.py is done")