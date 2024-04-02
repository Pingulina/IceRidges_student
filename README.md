# IceRidges Simulation

This simulation is based on the work by [Ilija Samardzija](https://github.com/ilijasam/IceRidges).

## Setting up the environment
To set up the python environment using conda run `initialize_python.py`. It will guide you through all necessary steps. Alternatively, set up your environment manually by using Anaconda Navigator as GUI or via the terminal. Then you have to install all necessary packages manually. A list of all packages can be found in `initialize_python.py`.

More information about setting up the environment including installation of python can be found in the [initliazation & preparation README](initialization_preparation/README.md) in the `initialization_preparation` folder.

## Running the code
### Data preparation
The data used is available on [Woods Hole Oceanographic Institution](https://www2.whoi.edu/site/beaufortgyre/data/mooring-data/) (Accessed on March 07, 2024). Please download the .dat files for all time slots you want to simulate. If you want to use your own data files, please make sure that they are in `.dat` format with columns `date` (int), `time` (int) and `draft` (float or double). Otherwise, you could use `.csv` files, but have to change the separation character as described in the README of `initialization_preparation`.
By running `S001_LoadData.py` the data files are loaded and stored as `.json` files to enable further use in the following code.

### Rayleigh Criteria to define where the ridges are located
To identify the different ice ridges, the Rayleigh Criteria is used. Rayleigh Criteria describes the minimal distance between to points to be seen as two independent points. Normally used in optics to describe the light fracturing and light bending, it can also be used as a definition for the independency of adjacent peaks.

### Structure the data for weekly storage
The data loaded in `S001_LoadData.py` is now structured for a weekly storage format. For every week, a set of variables is stored in a `dict`-structure and is stored as `.json` files afterwards.
The data stored is
```
LI_DM = [];         %   level ice estimate
LI_AM = [];         %   level ice estimate DEEPEST MODE
D = [];             %   deepest keel estimate
N = [];             %   number of ridges
M = [];             %   mean keel depth
T = [];             %   mean time in the week's subsample
WS = [];            %   week start timing
WE = [];            %   week end timing
D_all = [];         %   collection of all of the keels
T_all = [];         %   collection of all the times
Year = [];          %   year of the specific datapoint (week)
Location = [];      %   location of the specific datapoint (week)
Dmax = [];          %   maximum deel depth
PKSall = [];        %   all of the distribution's peaks values
LOCSall = [];       %   all of the distribution's peaks locations
```

The ridge positions and depths as well as the level ice thickness is are computed automatically, but may be reviewed manually.

### Review the determiation of level ice thickness 
Due to uncertainities, the automatical detection and computation of ice ridges and level ice may fail. Therefore, the level ice and ice ridge distributions have to be checked by the user. Using interactive plots, the user can refit the data directly for each week.

