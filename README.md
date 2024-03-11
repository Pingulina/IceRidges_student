# IceRidges Simulation

This simulation is based on the work by Ilija Samardzija [Link](https://github.com/ilijasam/IceRidges)

## Setting up the environment
To set up the python environment using conda run `initialize_python.py`. It will guide you through all necessary steps. Alternatively, set up your environment manually by using Anaconda Navigator as GUI or via the terminal. Then you have to install all necessary packages manually. A list of all packages can be found in `initialize_python.py`.

## Running the code
**Data preparation**
The data used is available on [Link](https://www2.whoi.edu/site/beaufortgyre/data/mooring-data/) (Accessed on March 07, 2024). Please download the .dat files for all time slots you want to simulate. If you want to use your own data files, please make sure that they are in `.dat` format with columns `date` (int), `time` (int) and `draft` (float or double).
By running `S001_LoadData.py` the data files are loaded and stored as `.json` files to enable further use in the following code.

---