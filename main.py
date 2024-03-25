# this is the main function for the ice ridge code
import os

import initialization_preparation.data2json as d2j
import initialization_preparation.initialize_python as init_py
import initialization_preparation.extract_ridge_LI_data as ewd
import initialization_preparation.data2dict as d2d
import ridge_computations.ridge_statistics as rs

def main():
    # init_py.initialize_python()
    # d2j.example() # store the .dat files as .json files for the mooring data
    ewd.extract_ridge_LI_data(overwrite=True)
    # rs.ridge_statistics()
    # d2d.example()
    return None

if __name__ == "__main__":
    main()