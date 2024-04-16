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
    import ridge_computations.ridge_statistics as rs
    import weekly_visual_analysis as wva
    # d2j.example() # store the .dat files as .json files for the mooring data

    # rs.ridge_statistics()
    # d2d.example()

    ### uncomment the following line to run the extract_ridge_LI_data.py file
    # ewd.extract_ridge_LI_data(overwrite=True)

    ### uncomment the following line to run the ridge_statistics.py file
    # dict_ridge_statistics = rs.ridge_statistics(years=[2005, 2006])
    # store the ridge statistics in a json file
    # with open('ridge_statistics.json', 'w') as file:
    #     json.dump(dict_ridge_statistics, file)


    # load the ridge statistics from the json file
    with open('ridge_statistics.json', 'r') as file:
        dict_ridge_statistics = json.load(file)
    wva.weekly_visual_analysis(dict_ridge_statistics)
    return None

if __name__ == "__main__":
    main()