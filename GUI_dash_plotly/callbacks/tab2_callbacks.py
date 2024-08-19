from dash import Output, Input, State, dcc, html
import json
import os
import sys

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants_original = import_module('constants_original', 'helper_functions')
constants = import_module('constants', 'helper_functions')
extract_ridge_LI_data = import_module('extract_ridge_LI_data', 'initialization_preparation')
ridge_statistics = import_module('ridge_statistics', 'data_analysis')
ridge_statistics_plot_plotly = import_module('ridge_statistics_plot_plotly', 'plot_functions')

### Callbacks for Tab 2
def register_tab2_callbacks(app):
    # Callback to handle the button click for extract ridge levelIce data in Tab 2
    @app.callback(
        Output('simulation-progress-output', 'children', allow_duplicate=True),
        Input('run-extract_ridge_LI_data-button', 'n_clicks'),
        State('selected-years-locations-store', 'data'),
        prevent_initial_call=True
    )
    def run_extract_ridge_LI_data(n_clicks, years_locs):
        if n_clicks > 0:
            feedback_message = 'Simulation is running...'
            extract_ridge_LI_data.extract_ridge_LI_data(terminal_use=False, dict_mooring_locations=years_locs)
            feedback_message = 'Simulation has been run. Check the console for output.'
            return feedback_message
        return ''

    # Callback to handle the button click for ridge statistics in Tab 2
    @app.callback(
        Output('ridge_statistics-output', 'children', allow_duplicate=True),
        Input('run-ridge_statistics-button', 'n_clicks'),
        State('selected-years-locations-store', 'data'),
        prevent_initial_call=True
    )
    def run_ridge_statistics(n_clicks, years_locs):
        if n_clicks > 0:
            ridge_statistics.ridge_statistics(years_locs_dict=years_locs, saveAsJson=True, run_as_app=True)
            with open(os.path.join(constants.pathName_dataResults, 'ridge_statistics', f"ridge_statistics_{2004}{'a'}.json"), 'r') as f:
                json_data = json.load(f)
            return 'Simulation has been run. Check the console for output.', json_data
        return '', {}