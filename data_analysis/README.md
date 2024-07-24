This documentation is only about the methods and files in data_analysis. The general documentation can be found in the [main README](../README.md).

# Initialization and preparation of the simulation

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


