from dash import Output, Input, State
import plotly.graph_objs as go
import json
import os
import sys
from copy import deepcopy

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
        prevent_initial_call=True
    )
    def load_json_data(n_clicks, json_data):
        if n_clicks > 0:
            if not 2004 in json_data:
                json_data[2004] = {}
            if not 'a' in json_data[2004]:
                json_data[2004]['a'] = {}
            with open(os.path.join(constants.pathName_dataResults, 'ridge_statistics', f"ridge_statistics_{2004}{'a'}.json"), 'r') as f:
                # load the data from the json file
                print(f)
                data_tmp = json.load(f)
            # add the current loaded data to the json_data dict; json_data contains data from ridge_statistics, LI_statistics, raw data etc.
            for key in data_tmp:
                json_data[2004]['a'][key] = deepcopy(data_tmp[key])
            return json_data
        return {}

    # Callback to update the plot for ridge statistics
    @app.callback(
        Output('plot-output', 'figure'),
        Input('render-plot-button', 'data'),
        State('json-data-store', 'data'),
    )
    def update_plot(n_clicks, json_data):
        if json_data:
            print('plotting')
            fig = ridge_statistics_plot_plotly.plot_per_location(json_data, year=2004, loc='a')
            return fig
        return go.Figure()