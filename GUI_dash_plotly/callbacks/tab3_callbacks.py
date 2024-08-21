from dash import Output, Input, State
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


### Callbacks for Tab 3
def register_tab3_callbacks(app):
    # here come the callbacks for the visualization tab
    # Callback to load the data from the JSON files
    @app.callback(
        Output('json-data-store', 'data'),
        Input('load-json-data-button', 'n_clicks'),
        State('json-data-store', 'data'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        prevent_initial_call=True
    )
    def load_json_data(n_clicks, json_data, season, loc):
        if n_clicks > 0:
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
            print('Data loaded from ridge statistics')
            # load the dateNum and draft data
            with open(os.path.join(constants.pathName_dataRaw, 'uls_data', f"mooring_{season}_{loc}_draft.json"), 'r') as f:
                data_tmp = json.load(f)
            print(data_tmp.keys())
            json_data[year][loc]['dateNum'] = deepcopy(np.array(data_tmp[loc]['dateNum']))
            json_data[year][loc]['draft'] = deepcopy(np.array(data_tmp[loc]['draft']))
            print('Data loaded from raw data')
            # load the dateNum_LI and draft_mode data
            with open(os.path.join(constants.pathName_dataRaw, 'uls_data', f"mooring_{season}_LI.json"), 'r') as f:
                data_tmp = json.load(f)
            json_data[year][loc]['dateNum_LI'] = deepcopy(np.array(data_tmp[loc]['dateNum']))
            json_data[year][loc]['draft_mode'] = deepcopy(np.array(data_tmp[loc]['draft']))
            json_data[year][loc]['draft_LI'] = deepcopy(np.array(data_tmp[loc]['draft']))
            print('LI data loaded from raw data')
            # load the dateNum_rc and draft_rc data
            with open(os.path.join(constants.pathName_dataRaw, 'uls_data', f"mooring_{season}_ridge.json"), 'r') as f:
                data_tmp = json.load(f)
            json_data[year][loc]['dateNum_rc'] = deepcopy(np.array(data_tmp[loc]['dateNum']))
            json_data[year][loc]['draft_rc'] = deepcopy(np.array(data_tmp[loc]['draft']))
            print('Ridge data loaded from raw data')
            # print(json_data)
            return json_data
        return {}

    # Callback to update the plot for ridge statistics
    @app.callback(
        Output('plot-output', 'figure'),
        Input('render-plot-button', 'n_clicks'),
        State('json-data-store', 'data'),
        State('season-plot-dropdown', 'value'),
        State('location-plot-dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_plot(n_clicks, json_data, season, loc):
        if json_data:
            print('update_plot')
            year = season.split('-')[0]
            fig = ridge_statistics_plot_plotly.plot_per_location(json_data[year], year=year, loc=loc)
            return fig
        return go.Figure()
    


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
