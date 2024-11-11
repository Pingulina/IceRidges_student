# Graphical user interface (GUI) for the IceRidges simulation
The graphical user interface (GUI) is your interface to the simulation. It allows you to set up the simulation, run it and visualize the results.

## Activate the environment
First, you have to activate the conda environment you created before.

**On unix-based systems (e.g. macOS and Linux):** Open the terminal and activate the conda environment by typing 
```bash
conda activate IceRidges
```
Replace `IceRidges` with the name of your conda environment, if you named it differently. 

**On Windows:** Open the Anaconda Powershell Promt via the Anaconda Navigator. First, choose the correct environment in the Anaconda Navigator, then open the Powershell Promt. Like that, the environment is activated automatically.

## Starting the GUI

Navigate to the `IceRidges_student` folder by typing the following commands in the terminal:
```bash
cd Documents/IceRidges # navigate to the folder where the code is stored
cd IceRidges_student # navigate to the IceRidges_student folder
```
and start the GUI by typing 
```bash
python GUI_dash_plotly/app.py # run the app.py file, located in the GUI_dash_plotly folder
```
To open the GUI in your browser, open the link that is shown in the terminal. 


## Stopping the GUI
To stop the GUI, you have to kill the process in the terminal by pressing `ctrl` + `c`. There might be a better way in the future, but for now, you have to kill the process manually.

## Using the GUI
The GUI consists of four tabs: `Settings`, `Simulation`, `Vizualization` and `Load (independent)`.
A general note: Some of the operations start slightly time-consuming calculations. Please be patient and wait for the calculations to finish. The GUI will inform you when the calculations are done, either by a message or by stopping the loading animation.
Do **NOT** close or reload your browser window while the calculations are running. This will cause trouble and you have to restart the GUI and some of the results might be lost.
### Settings
In the first tab, the settings for the simulation are defined. The most important things for you is to chose the seasons and locations you want to work on. First, chose a season from the dropdown menu. Then tick all locations you want to work on. Click on `Add selected year and location(s)` afterwards. You can add as many seasons and locations as you want. If you want to remove a location, select the corresponding season again and then untick the location. If you untick all locations, the season will be removed from the list. Allways click on `Add selected year and location(s)` after you made changes to the selection (also after unticking locations).

The table at the bottom of the tab shows the parameters used in the simulation. You don't have to make changes her, unless you are using another data set than the one described [before](/README.md#data).

### Simulation
In the second tab, you can run the different simulations. You have to chose the seasons and locations in the first tab before running any simulations.

In the first step, you have to transform the `.dat` files to `.json` files. This is done by clicking on the `Transform data` button. It might take multiple minutes per location and year, so be patient. When you click on `Show transformed data`, you can see a list of all the data that has been transformed.

In the second step, you have to extract the ridges and level ice sequences from the data. This is done by clicking on the `Extract data` button. It might take multiple minutes per location and year, so be patient.
When you click on `Show extracted data`, you can see a list of all the data that has been extracted.

The third step is to do some ridge statistics. This is done by clicking on the `Find ridges` button. This step might take a while, so be patient. When you click on `Show computed ridge data`, you can see a list of all the ridges that have been found.

More steps will be added in the future.

### Visualization
In the third tab, you can visualize the results of the simulation. On the top of the tab, you have to chose the season and location from the dropdown menus you want to visualize. Then click on `Load JSON Data`. This will load the data from the simulation. You will get a message, when the data is loaded. Then you can chose the visualization you want to see. For some of the visualizations, you have to set additional parameters or load additional data. The GUI will guide you through the process.

### Load (independent)
The last tab can be used independently from the first three tabs. It is used to compute the load distribution on fixed structures by ice ridges. Instead of a full simulation of the ice ridges, the distributions described by [Ilija Samardzija](https://doi.org/10.1016/j.coldregions.2023.104021) are used. Enter the values for the diameter of the structure and the number of years to simulate. Then click on `Load simulations`. The results will be vizalized below. You can change the values and click on `Load simulations` again to see the results for different values.
