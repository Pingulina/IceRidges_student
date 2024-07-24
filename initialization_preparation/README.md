This documentation is only about the needed initialization and preparation. The general documentation can be found in the [main README](../README.md).

# Initialization and preparation of the simulation
The files in this package are used to set up the Python environment and prepare the needed data (e.g. storing into json files, etc.)
This package is no stand-alone package. Therefore, it needs to be run from the currend working directory (`IceRidges_python`), otherwise some general files are not found.

## Set up the Python environment
To set up the Python environment, the function `initialize_python.py` can be used. It requires a `conda` environment, then all needed packages are installed via `conda` automatically. It is recommended to use Anaconda to set up the Python environment. The simulation was set up by using `Python3.11.8`. \
Setting up the environment via `pip` is also possible. Then the necessary packages must be installed manually.
The packages used are 
``` 
    numpy
    matplotlib
    conda-forge::pynput
    json
    datetime
    sys
    scipy
    pandas
```

To set up the `conda` environment, it is recommended to use [Anaconda](https://www.anaconda.com/download). Download and install Anaconda, all other steps are covered by `initialize_python.py`.

## Preparation of the simulation
### Storing of data
To enable the simulation, the data must be transformed to a readable format. The `.dat` files are already readable.

### Getting all mooring locations
Based an all `.dat` files found in the `mooring_data` folder, the abreviations (`'a'`, `'b'`, etc.) as well as the corresponding positions in latitude and longitude are written to a dict, which is then stored as `.json`. If there is already such a `.json` file, the user is asked if this file should be used or if a new one should be generated (which will overwrite the existing one).

### Old version of transformation to json files
The file `data2json.py` can be used to load the `.dat` files with the mooring data (e.g. downloaded from [Woods Hole Oceanographic Institution](https://www2.whoi.edu/site/beaufortgyre/data/mooring-data/) as described in the [main documentation](/README.md)) and preparing them for further processes.

Therefore, the `.dat` files containing the data are loaded into a Python dictionary and then stored as `.json` files. 
The module `data2json.py` contains different functions. `data2json(file_path, file_name, storage_path)` loads a whitespace seperated data file and stores it as `.json` file. The name of the file stays the same. The path of the new `.json` file as well as of the exsiting `.dat` file are used as input parameters `storage_path` and `file_path`.
To enable reading `.csv` data instead, the separation symbol needs to be changed from `''` to `','`.

The function `data2json_multi(file_path_list, storage_path_folder)` transforms all files named in `file_path_list` and stores them as `.json` files in the folder named in `storage_path_folder`. Existing files with the same name are overwritten without asking.

To decide if the exisiting files should be overwritten, the function `data2json_interactive(file_path_list, storage_path_folder, overwrite=None)` should be used. If the optional parameter `overwrite` is not set, the user will be asked for every existing file, if it should be overwritten or skipped. If `overwrite=True`, all exsiting files will be overwritten without asking (same behaviour as `data2json_multi`, but less efficient due to additional if statements). If `overwrite=False`, all exisiting files will be skipped. The latter one is the most efficient way to transform all new data files to `.json` files.

## Preprocessing of measured data
The file [`extract_ridge_LI_data.py`](/initialization_preparation/extract_ridge_LI_data.py) contains a method, that determines the time steps, where ridges occur and prepares the data set for a weekly-based evaluation. 

First, the possible mooring locations covered by the data are determined and stored in a dictionary. This is done by `mooring_locations()` with the optional keyword `storage_path` from the file `mooring_locations.py`. The dictionary contains information about the mooring positions with its positions (latitude and longitude) for every year. If `storage_path` is given to `mooring_locations()`, the dictionary is also stored as a `.json` file. If such a file already exists, the user is asked if this file should be used or overwritten by a new one. 

> If the data hasn't changed since the last creation of the `mooring_locations.json` file, it is recommended to use the existing file to save computation time.

In the next step, the user has to decide, if all locations and years from the loaded `dict_mooring_locations` should be used or if the user wants to choose only specific years and locations. All interaction is done via the terminal, instructions are also given via the terminal. If the years and locations are changed, the `dict_mooring_locations` is updated. This doesn't affect the stored `mooring_locations.json`.

In the `extract_ridge_LI_data` function, the core processing is encapsulated within nested for loops that iterate through the dataset's temporal and spatial dimensions. The outer loop traverses through each season or year specified in `dict_mooring_locations`, effectively segmenting the data analysis on a temporal basis.

> `year`is used, if the expression consists of one number (e.g. 2005), while `season` is used if the time span of the data measurement is described (e.g. 2005-2006). 

Within each iteration of this outer loop, the inner loop iterates over all specified mooring locations for the current season or year, allowing for a spatial breakdown of the data analysis. This dual-loop structure facilitates a comprehensive examination of the dataset, where for each season or year, and for each location, the function identifies and processes ridge and level ice (LI) data separately.
The ridges are identified using the Rayleigh Criteria, which defines the minimum distance between two points to be considered independent. This criterion is applied to the draft data to identify the ridges, which are then together with the corresponding time data stored in the `dict_draft_ridge` dictionary. The level ice data is reshaped draft and time data: every row contains data from one week and stored in the `dict_draft_LI` dictionary. The raw data is stored in the `dict_draft` dictionary, which contains the unprocessed draft and time data.

> To express the time, the datenum format is used. The unit of datenum is days and it is the time passed since January 01 0001.

The processed data for each category — unprocessed draft and time data (`dict_draft`), ridge data (`dict_draft_ridge`), and level ice data (`dict_draft_LI`) — are stored in distinct dictionaries. This methodical approach ensures that the analysis is both temporally and spatially organized, providing a clear and structured dataset for subsequent weekly-based evaluation and analysis.



