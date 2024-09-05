from dash import Output, Input, State, Patch
import plotly.graph_objs as go
import json
import os
import sys
from copy import deepcopy
import numpy as np

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants_original = import_module('constants_original', 'helper_functions')
constants = import_module('constants', 'helper_functions')
extract_ridge_LI_data = import_module('extract_ridge_LI_data', 'initialization_preparation')
ridge_statistics = import_module('ridge_statistics', 'data_analysis')
ridge_statistics_plot_plotly = import_module('ridge_statistics_plot_plotly', 'plot_functions')
weekly_analysis_plot_plotly = import_module('weekly_analysis_plot_plotly', 'plot_functions')
weekly_analysis_plot_plotly_update = import_module('weekly_analysis_plot_plotly_update', 'plot_functions')


### Callbacks for Tab 3
def register_tab3_callbacks(app):
    # here come the callbacks for the visualization tab
    # Callback to update the season dropdown
    @app.callback(
        Output('season-plot-dropdown', 'options'),
        #[Input('ridge_statistics-output', 'data'),
         Input('tabs-all', 'value'),
    )
    def update_seasons_dropdown(tab):
            if tab == 'tab-3':
                # list all files in data_analysis/ridge_statistics
                files = os.listdir(os.path.join(constants.pathName_dataResults, 'ridge_statistics'))
                # load the data/mooring_locations.json file, then get the corresponding season to the year
                with open(os.path.join(constants.pathName_dataRaw, 'mooring_locations.json'), 'r') as f:
                    mooring_locs = json.load(f)
                seasons = []
                all_seasons = list(mooring_locs.keys())
                for file in files:
                    if file.endswith('.json'):
                        year = file.split('_')[2][:4]
                        season = all_seasons[np.where([year == this_season.split('-')[0] for this_season in all_seasons])[0][0]]
                        seasons.append(season)
                seasons = list(set(seasons))
                seasons.sort()
                return [{'label': season, 'value': season} for season in seasons]
            return []
    # Callback to update the location dropdown based on the selected season
    @app.callback(
        Output('location-plot-dropdown', 'options'),
        Input('season-plot-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_location_dropdown(season):
        files = os.listdir(os.path.join(constants.pathName_dataResults, 'ridge_statistics'))
        locations = []
        year = season.split('-')[0]
        for file in files:
            if file.endswith('.json') and file.split('_')[2][:4] == year:
                locations.append(file.split('_')[2][4])
        return [{'label': location, 'value': location} for location in locations]

    # Callback to load the data from the JSON files
    @app.callback(
        Output('json-data-store', 'data'),
        Output('confirm', 'displayed', allow_duplicate=True),
        Output('confirm', 'message', allow_duplicate=True),
        Input('load-json-data-button', 'n_clicks'),
        State('json-data-store', 'data'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        prevent_initial_call=True
    )
    def load_json_data(n_clicks, json_data, season, loc):
        if n_clicks > 0:
            if season is None or loc is None:
                return {}, True, 'Please select a season and a location'
            year = season.split('-')[0]
            if not year in json_data:
                json_data[year] = {}
            if not loc in json_data[year]:
                json_data[year][loc] = {}
            with open(os.path.join(constants.pathName_dataResults, 'ridge_statistics', f"ridge_statistics_{year}{loc}.json"), 'r') as f:
                # load the data from the json file
                data_tmp = json.load(f)
            # add the current loaded data to the json_data dict; json_data contains data from ridge_statistics, LI_statistics, raw data etc.
            for key in data_tmp:
                json_data[year][loc][key] = deepcopy(data_tmp[key])
            # print('Data loaded from ridge statistics')
            # load the dateNum and draft data
            with open(os.path.join(constants.pathName_dataRaw, 'uls_data', f"mooring_{season}_{loc}_draft.json"), 'r') as f:
                data_tmp = json.load(f)
            # print(data_tmp.keys())
            json_data[year][loc]['dateNum'] = deepcopy(np.array(data_tmp[loc]['dateNum']))
            json_data[year][loc]['draft'] = deepcopy(np.array(data_tmp[loc]['draft']))
            # print('Data loaded from raw data')
            # load the dateNum_LI and draft_mode data
            with open(os.path.join(constants.pathName_dataRaw, 'uls_data', f"mooring_{season}_LI.json"), 'r') as f:
                data_tmp = json.load(f)
            json_data[year][loc]['dateNum_LI'] = deepcopy(np.array(data_tmp[loc]['dateNum']))
            json_data[year][loc]['draft_mode'] = deepcopy(np.array(data_tmp[loc]['draft']))
            json_data[year][loc]['draft_LI'] = deepcopy(np.array(data_tmp[loc]['draft']))
            # print('LI data loaded from raw data')
            # load the dateNum_rc and draft_rc data
            with open(os.path.join(constants.pathName_dataRaw, 'uls_data', f"mooring_{season}_ridge.json"), 'r') as f:
                data_tmp = json.load(f)
            json_data[year][loc]['dateNum_rc'] = deepcopy(np.array(data_tmp[loc]['dateNum']))
            json_data[year][loc]['draft_rc'] = deepcopy(np.array(data_tmp[loc]['draft']))
            # print('Ridge data loaded from raw data')
            # print(json_data)
            return json_data, True, 'Successfully loaded the data. You can now continue with the next steps.'
        return {}, False, ''

    # Callback to update the plot for ridge statistics
    @app.callback(
        Output('plot-ridges', 'figure'),
        # Output('plot-json-ridges-store', 'data'),
        Output('confirm', 'displayed', allow_duplicate=True),
        Output('confirm', 'message', allow_duplicate=True),
        Input('render-plot-button', 'n_clicks'),
        State('json-data-store', 'data'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_plot_ridges(n_clicks, json_data, season, loc):
        if n_clicks > 0:
            if not json_data:
                return go.Figure(), True, 'No data loaded. Please load the data first'
            if season is None or loc is None:
                return go.Figure(), True, 'Please select a season and a location'
            print('update_plot')
            print(season)
            year = season.split('-')[0]
            fig = ridge_statistics_plot_plotly.plot_per_location(json_data[year], year=year, loc=loc)
            fig_json = fig.to_json()
            return fig, False, ''
            # return fig_json
        return go.Figure(), False, ''
        # return go.Figure().to_json()


    # Callback to load the data for weekly analysis and correction
    @app.callback(
        Output('json-data-allRidges_allYears-store', 'data'),
        Output('confirm', 'displayed', allow_duplicate=True),
        Output('confirm', 'message', allow_duplicate=True),
        Input('load-weekly-analysis-button', 'n_clicks'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        prevent_initial_call=True
    )
    def load_weekly_analysis_data(n_clicks, season, loc):
        if n_clicks > 0:
            print('load weekly analysis data')
            year = int(season.split('-')[0])
            # load the weekly analysis data
            dict_ridge_statistics_allYears = weekly_analysis_plot_plotly.weekly_analysis_load_data_all_years()
            return dict_ridge_statistics_allYears, True, 'Successfully loaded the additional data. You can now render the plot.'
        return None, False, ''

    # Callback to render the weekly analysis plot
    @app.callback(
        Output('plot-weekly-analysis', 'figure', allow_duplicate=True),
        Output('json-trace-indices-store', 'data'),
        Output('confirm', 'displayed', allow_duplicate=True),
        Output('confirm', 'message', allow_duplicate=True),
        Input('render-weekly-analysis-button', 'n_clicks'),
        State('json-data-store', 'data'),
        State('json-data-allRidges_allYears-store', 'data'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        State('week-slider', 'value'),
        prevent_initial_call=True
    )
    def plot_weekly_analysis_plot(n_clicks, json_data, dict_ridge_statistics_allYears, season, loc, week):
        if n_clicks > 0:
            if not json_data:
                print(json_data)
                return go.Figure(), {}, True, 'No data loaded. Please load the data first'
            if season is None or loc is None:
                return go.Figure(), {}, True, 'Please select a season and a location'
            if dict_ridge_statistics_allYears is None:
                return go.Figure(), {}, True, 'No additional data loaded. Please load the additional data first'
            print('plot weekly analysis')
            year = int(season.split('-')[0])
            week = week -1 # because the slider starts at 1 (to make it more user-friendly for people without programming/informatics background)
            fig, dict_trace_indices = weekly_analysis_plot_plotly.weekly_analysis_plot(year, loc, week, dict_ridge_statistics_allYears, json_data)
            print('weekly analysis plot initialized')
            return fig, dict_trace_indices, False, ''
        return go.Figure(), {}, False, ''

    # # Callback to update the plot for weekly analysis and correction
    # @app.callback(
    #     Output('plot-weekly-analysis', 'figure', allow_duplicate=True),
    #     Output('confirm', 'displayed', allow_duplicate=True),
    #     Output('confirm', 'message', allow_duplicate=True),
    #     Input('week-slider', 'value'),
    #     State('json-data-store', 'data'),
    #     State('json-data-allRidges_allYears-store', 'data'),
    #     State('season-plot-dropdown', 'value'),
    #     State('location-plot-dropdown', 'value'),
    #     State('plot-weekly-analysis', 'figure'),
    #     State('json-trace-indices-store', 'data'),
    #     prevent_initial_call=True
    # )
    # def update_weekly_analysis_plot(week, json_data, dict_ridge_statistics_allYears, season, loc, fig, dict_trace_indices):
    #     print('update weekly analysis plot')
    #     week = week -1 # because the slider starts at 1 (to make it more user-friendly for people without programming/informatics background)
    #     if json_data and season and loc:
    #         year = season.split('-')[0]
    #         # Assuming you have a function to generate the weekly analysis plot week, year, loc, fig, dict_ridge_statistics_allYears, dict_ridge_statistics_jsonified, dict_trace_indices
    #         fig, display_confirm, message_confirm = weekly_analysis_plot_plotly_update.weekly_analysis_update_plot(year, loc, week, fig, dict_ridge_statistics_allYears, json_data[year], dict_trace_indices)
    #         return fig, display_confirm, message_confirm
    #     return go.Figure(), False, ''
    
    # Callback to update the plot for weekly analysis and correction partially
    @app.callback(
        Output('plot-weekly-analysis', 'figure', allow_duplicate=True),
        Output('confirm', 'displayed', allow_duplicate=True),
        Output('confirm', 'message', allow_duplicate=True),
        Input('week-slider', 'value'),
        State('json-data-store', 'data'),
        State('json-data-allRidges_allYears-store', 'data'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        State('json-trace-indices-store', 'data'),
        prevent_initial_call=True
    )
    def update_weekly_analysis_plot_partially(week, json_data, dict_ridge_statistics_allYears, season, loc, dict_trace_indices):
        week = week -1 # because the slider starts at 1 (to make it more user-friendly for people without programming/informatics background)
        if json_data and season and loc:
            print('update weekly analysis plot partially')
            # Create a patch object
            patch = Patch()
            year = season.split('-')[0]
            # Update the current week patch in the figure
            patch, display_confirm, message_confirm = weekly_analysis_plot_plotly_update.weekly_analysis_update_plot(year, loc, week, patch, dict_ridge_statistics_allYears, json_data[year], dict_trace_indices)
            return patch, display_confirm, message_confirm
        return go.Figure(), False, ''
    

    ## Callbacks to correct specified values
    # Callback to chose a value
    @app.callback(
        Output('value-to-correct', 'data'),
        Input('click-value', 'data'), # this variable is to store the clicked value in the plot
    )
    def get_value_to_correct(click_value):
        return click_value
    

    @app.callback(
        Output('corrected-value', 'data'),
        Output('json-data-store', 'data', allow_duplicate=True),
        Input('navigation-arrows', 'value'),
        State('value-to-correct', 'data'),
        State('json-data-store', 'data'),
        prevent_initial_call=True
    )
    def correct_value(navigation, value_id, json_data):
        corrected_value = json_data[value_id] # TODO: need to implement correction
        # idea: navigation consists of value for the up and down arrows to correct the value in steps. Or with direct entry field.
        return corrected_value, json_data
        
    

