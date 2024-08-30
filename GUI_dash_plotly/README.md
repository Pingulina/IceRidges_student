# Graphical user interface (GUI) for the IceRidges simulation
The graphical user interface (GUI) is your interface to the simulation. It allows you to set up the simulation, run it and visualize the results.
## Starting the GUI
To start the GUI, you have to navigate to the `IceRidges_student` folder and run the `gui.py` script.

Open the terminal and activate the conda environment by typing 
```bash
conda activate IceRidges
```
Replace `IceRidges` with the name of your conda environment, if you named it differently. Navigate to the `IceRidges_student` folder 
```bash
cd Documents/IceRidges/IceRidges_student # navigate to the folder where the code is stored
```
and start the GUI by typing 
```bash
python app.py
```
To open the GUI in your browser,open the link that is shown in the terminal. 


## Stopping the GUI
To stop the GUI, you have to kill the process in the terminal by pressing `ctrl` + `c`. There might be a better way in the future, but for now, you have to kill the process manually.

## Using the GUI
The GUI consists of three tabs: `Settings`, `Simulation` and `Vizualization`.
A general note: Some of the operations start slightly time-consuming calculations. Please be patient and wait for the calculations to finish. The GUI will inform you when the calculations are done, either by a message or by stopping the loading animation.
Do **NOT** close or reload your browser window while the calculations are running. This will cause trouble and you have to restart the GUI and some of the results might be lost.
### Settings
In the first tab, the settings for the simulation are defined. The most important things for you is to chose the seasons and locations you want to work on. First, chose a season from the dropdown menu. Then tick all locations you want to work on. Click on `Add selected year and location(s)` afterwards. You can add as many seasons and locations as you want. If you want to remove a location, select the corresponding season again and then untick the location. If you untick all locations, the season will be removed from the list. Allways click on `Add selected year and location(s)` after you made changes to the selection (also after unticking locations).

The table at the bottom of the tab shows the parameters used in the simulation. You don't have to make changes her, unless you are using another data set than the one described [before](/README.md#data).

### Simulation
In the second tab, you can run the different simulations. You have to chose the seasons and locations in the first tab before running any simulations.

In the first step, you have to extract the data from the `.dat` files. This is done by clicking on the `Extract data` button. It might take multiple minutes per location and year, so be patient.
When you click on `Show extracted data`, you can see a list of all the data that has been extracted.

The second step is to find the ridges in the data. This is done by clicking on the `Find ridges` button. This step might take a while, so be patient. When you click on `Show computed ridge data`, you can see a list of all the ridges that have been found.

More steps will be added in the future.

### Visualization
In the third tab, you can visualize the results of the simulation. On the top of the tab, you have to chose the season and location from the dropdown menus you want to visualize. Then click on `Load JSON Data`. This will load the data from the simulation. You will get a message, when the data is loaded. Then you can chose the visualization you want to see. For some of the visualizations, you have to set additional parameters or load additional data. The GUI will guide you through the process.


