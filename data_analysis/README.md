This documentation is only about the methods and files in data_analysis. The general documentation can be found in the [main README](../README.md).

# Data analysis

## Ridge statistics
[`ridge_statistics.py`](/data_analysis/ridge_statistics.py) provides a method for analyzing ice ridge data on a weekly basis, extracting key statistics and insights into the temporal distribution and characteristics of ice ridges. The method systematically processes the ridge data, calculating metrics such as the number of ridges, average and maximum ridge depths, and identifying the most common ridge depth for each week. This analysis contributes to a comprehensive understanding of ridge dynamics over time.
Here's a breakdown of its functionality:

#### Weekly Data Extraction: 
For each week in the dataset, the method extracts ridge data (`draft_rc_reshape`) and corresponding dates (`dateNum_rc_reshape`) for that week. This is achieved through the `extract_weekly_data_draft_ridge` function, which segments the data into weekly intervals based on the `dateNum_reshape` and `draft_reshape` arrays.

#### Ridge Count: 
The number of ridges for each week is calculated and stored in `R_no[week_num]`, providing a count of ridges observed within each weekly segment.

#### Subset of Raw ULS Draft Measurement:
A subset of the draft measurements is selected based on specific criteria (draft values between 0 and 3 meters) and within the time frame of the current week. This subset is used for further statistical analysis.

#### Weekly Data Validation: 
Weeks with fewer than 6 ridge data points or no valid draft measurements are skipped, as they are considered to have insufficient data for reliable analysis.

#### Statistical Calculations:
The mean date (`dateNum_rc_pd[week_num]`) and mean keel draft (`mean_keel_draft[week_num]`) for ridges within the week are calculated.
The maximum draft value (`draft_max_weekly[week_num]`) for the week is identified, representing the deepest ridge observed.
Kernel Density Estimate (KDE): A kernel density estimate is performed on the subset of draft measurements to estimate the probability density function (PDF) of the draft data. This KDE provides a smooth estimate of the draft distribution within the week.

#### Mode Analysis:
Peaks in the KDE are identified using `scipy.signal.find_peaks`, representing potential modes in the draft distribution.
The mode with the deepest draft is determined by finding the peak with the highest draft value that also meets a certain intensity threshold. This mode (`deepest_mode_weekly[week_num]`) represents the most common draft depth for the week, provided it passes the intensity threshold.
Data Filtering: Weeks without significant modes or with insufficient data are marked for exclusion from further analysis by setting `week_to_keep[week_num]` to False.



## Weekly Visual Analysis

The [`weekly_visual_analysis.py`](/data_analysis/weekly_visual_analysis.py) script is designed for performing and visualizing weekly analysis of ice ridge data. It utilizes matplotlib for plotting and provides insights into various metrics related to ice ridges over time. The script is structured to work with specific data formats, typically involving measurements of ice ridges, such as their number, depth, and distribution within a given time frame.
`weekly_visual_analysis()` is a comprehensive function for visualizing and analyzing weekly ice ridge data. Here's an overview of its functionality:

### Data Preparation
Data is prepared in the previous steps ([`extract_ridge_LI_data()`](/initialization_preparation/extract_ridge_LI_data.py) and [`ridge_statistics()`](/data_analysis/ridge_statistics.py)) is loaded and visualized. 
First, the data for one year is loaded using [`load_data()`](/data_handling/load_data.py). In this function, the user is asked to select year and location.

### Visualization 
The script generates a series of plots to visualize the weekly ice ridge data. These plots include:
- Ice draft data over time
- Ice draft data over time for one week
- Mean keel depth over level ice thickness
- Overview of the observed peaks in the draft distribution for one week
- Deepest ice draft per week over level ice thickness
- Number of ridges per week over level ice thickness

The user can then iterate through the weeks to view the corresponding plots and analyze the trends and patterns in the ice ridge data.

### Further Analysis
The script may include additional sections for further analysis and visualization, such as trends over time, comparisons between years, and statistical analysis of the data.


## Weekly Manual Correction

The `weekly_manual_correction.py` script is designed to perform manual corrections on weekly ice ridge data. This script is crucial for ensuring the accuracy of the data by allowing users to manually adjust and validate the measurements.

### Key Components

#### Plotting and Data Visualization
The script includes several plotting functions to visualize different aspects of the ice ridge data. These plots help in comparing the current year's data with historical data, making it easier to identify anomalies or trends.

1. **Spectrogram Plot**:
    Plots the spectrogram for the current week, highlighting the level ice deepest mode and expected deepest mode.

2. **Mean Ridge Keel Depth Plot**:
    Compares the mean ridge keel depth for the current week with historical data.

3. **Kernel Estimate Plot**:
    Plots the kernel estimate for the draft data, showing the distribution of ice ridge depths.

4. **Weekly Deepest Ridge Plot**:
    Visualizes the deepest ridge for the current week compared to historical data.

5. **Number of Ridges Plot**:
    Shows the number of ridges for the current week and compares it with historical data.

#### Manual Correction
The script includes a manual correction section where users can interactively adjust the data points for the current week. This is done using keyboard inputs to navigate and modify the data.

- **Controls**:
    - `6`: Increase value by 1
    - `4`: Decrease value by 1
    - `8`: Increase value by 5
    - `2`: Decrease value by 5
    - `-`: Delete value
    - `5`: Correct value/enter
    - `0`: Apply changes

    > It is recommende to use the numpad for a better experience.

- **Process**:
    - The script prints a message indicating the start of the manual correction process.
    - Users can navigate through the data points using the specified controls.
    - Changes are stored in a list of indices to be deleted or modified.
    - The loop continues until the user finalizes the corrections.

This manual correction process ensures that any anomalies or errors in the data can be addressed, leading to more accurate and reliable analysis.


## Preliminary Analysis and first Simulations

The `preliminary_analysis_simulation` function in [`preliminary_analysis_simulation.py`](/data_analysis/preliminary_analysis_simulation.py) is designed to perform an initial analysis of simulation data. It focuses on understanding the distribution and key statistical properties of the data. The function includes various methods to calculate statistical metrics such as mean, median, standard deviation, skewness, and kurtosis. Additionally, it provides visualization tools like histograms, density plots, and scatter plots to help identify patterns, anomalies, and overall behavior of the simulation results.

By conducting this preliminary analysis, the function helps users gain insights into the initial characteristics of the data, which can guide further detailed analysis. This early stage of data examination is crucial for identifying any potential issues or trends that need to be addressed, ensuring that subsequent analyses are based on accurate and well-understood data.

The `preliminary_analysis_simulation` function begins by loading the simulation data, which is typically stored in a variable named distribution. It then performs various statistical analyses to summarize the key properties of the data, including calculations for mean, median, standard deviation, skewness, and kurtosis. Following the statistical analysis, the function generates visualizations such as histograms, density plots, and scatter plots to help identify patterns and anomalies in the data. These visualizations and statistical summaries provide an initial understanding of the data's distribution and characteristics, guiding further detailed analysis.

## Leve Ice Statistics
The `level_ice_statistics` function in `level_ice_statistics.py` is designed to analyze level ice data and determine the level ice mode for each week. It begins by importing necessary libraries and modules, including NumPy, Matplotlib, and SciPy, as well as several custom modules using a helper function `import_module` to import from different directories. The function starts by loading a dictionary of mooring locations using the `mooring_locs module. This dictionary contains the mooring locations stored in a specified` path, which is essential for the subsequent analysis.

The function then prompts the user to input a year and location for the analysis if they are not provided as arguments. It ensures that the input year is valid by checking it against the available years in the mooring data. This setup prepares the script to perform further analysis on the level ice data based on the specified year and location. The function's primary goal is to analyze the level ice data and determine the level ice mode for each week, providing valuable insights into the ice conditions over time.

### Key Steps
The key steps involved in the `level_ice_statistics` function of `level_ice_statistics.py` are:

1. If the year and location are not provided as arguments, the user is prompted to input them. The function then checks the validity of the input year by comparing it to the available years in the mooring data.

2. The function loads the ice data for the specified year and location using the `load_data_one_year` function. Data, that is not stored directly is then computed directly.

3. To visualize the data, a figure with multiple plots is generated. Some of them show further insights into the weekly and daily data.

4. To iterate the weeks and days, follow the instructions in the terminal. The user can navigate through the weeks and days using 's', 'd', 'f' an 'x' to exit the loop. Every entry has to be confirmed by pressing 'enter'.