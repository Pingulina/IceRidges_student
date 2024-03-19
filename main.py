# this is the main function for the ice ridge code
import os

import initialization_preparation.data2json as d2j
import initialization_preparation.initialize_python as init_py
import initialization_preparation.extract_weekly_data as ewd
import ridge_computations.ridge_statistics as rs

def main():
    # init_py.initialize_python()
    # d2j.example() # store the .dat files as .json files for the mooring data
    ewd.extract_weekly_data(years=[2004, 2005, 2006], overwrite=True)
    rs.ridge_statistics()
    return None

if __name__ == "__main__":
    main()