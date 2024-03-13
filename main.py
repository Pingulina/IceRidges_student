# this is the main function for the ice ridge code
import os

import initialization_preparation.data2json as d2j
import initialization_preparation.initialize_python as init_py

def main():
    init_py.initialize_python()
    # d2j.example()
    return None

if __name__ == "__main__":
    main()