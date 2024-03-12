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
```

## Preparation of the simulation
To enable the simulation, the data must be transformed to a readable format. Therefore, the `.dat` files containing the data are loaded into a Python dictionary and then stored as `.json` files. 
The module `data2json.py` contains different functions. `data2json(file_path, file_name, storage_path)` loads a whitespace seperated data file and stores it as `.json` file. The name of the file stays the same. The path of the new `.json` file as well as of the exsiting `.dat` file are used as input parameters.
To enable reading `.csv` data instead, the separation symbol needs to be changed from `''` to `','`.

The function `data2json_multi(file_path_list, storage_path_folder)` transforms all files named in `file_path_list` and stores them as `.json` files in the folder named in `storage_path_folder`. Existing files with the same name are overwritten without asking.

To decide if the exisiting files should be overwritten, the function `data2json_interactive(file_path_list, storage_path_folder, overwrite=None)` should be used. If the optional parameter `overwrite` is not set, the user will be asked for every existing file, if it should be overwritten or skipped. If `overwrite=True`, all exsiting files will be overwritten without asking (same behaviour as `data2json_multi`, but less efficient due to additional if statements). If `overwrite=False`, all exisiting files will be skipped. The latter one is the most efficient way to transform all new data files to `.json` files.