from dash import Output, Input, State, dcc, html
import json
import os
import sys
import datetime
import time

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants_original = import_module('constants_original', 'helper_functions')
constants = import_module('constants', 'helper_functions')
extract_ridge_LI_data = import_module('extract_ridge_LI_data', 'initialization_preparation')
ridge_statistics = import_module('ridge_statistics', 'data_analysis')
ridge_statistics_plot_plotly = import_module('ridge_statistics_plot_plotly', 'plot_functions')
helping_functions = import_module('helping_functions', 'GUI_dash_plotly')
d2j = import_module('data2json', 'initialization_preparation')

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
            tic = time.time()
            feedback_message = 'Simulation is running...'
            path_name = constants.pathName_mooring_data
            file_path_list = [path_name.replace('SEASON', thisSeason) for thisSeason in ['2004-2005', '2005-2006', '2006-2007']] # ['2004-2005', '2005-2006', '2006-2007']]
            this_file_path = os.path.abspath(os.getcwd())
            storage_path_folder = os.path.join(this_file_path, 'Data', 'mooring_data')
            print('extract data to json')
            d2j.data2json_dict(storage_path_folder, years_locs)
            print('extract ridge data')
            extract_ridge_LI_data.extract_ridge_LI_data(terminal_use=False, dict_mooring_locations=years_locs)
            feedback_message = 'Simulation has been run. Check the console for output.'
            toc = time.time()
            print(f"Time taken for run_extract_ridge_LI_data: {toc-tic}")
            return feedback_message
        return ''
    
    # def run_extract_ridge_LI_data(n_clicks, years_locs):
    #     if n_clicks > 0:
    #         feedback_message = 'Simulation is running...'
    #         extract_ridge_LI_data.extract_ridge_LI_data(terminal_use=False, dict_mooring_locations=years_locs)
    #         feedback_message = 'Simulation has been run. Check the console for output.'
    #         return feedback_message
    #     return ''
    

    # Callback to handle the button click for showing the extracted data in Tab 2
    @app.callback(
        Output('confirm', 'message', allow_duplicate=True),
        Output('confirm', 'displayed', allow_duplicate=True),
        Input('show-extracted-data-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_extracted_data(n_clicks):
        if n_clicks:
            return helping_functions.find_data_in_folder(os.path.join(constants.pathName_dataRaw, 'uls_data'))
        return "", False

    # Callback to handle the button click for ridge statistics in Tab 2
    @app.callback(
        Output('simulation-progress-output', 'children', allow_duplicate=True),
        Output('ridge_statistics-output', 'data'),
        Input('run-ridge_statistics-button', 'n_clicks'),
        State('selected-years-locations-store', 'data'),
        prevent_initial_call=True
    )
    def run_ridge_statistics(n_clicks, years_locs):
        if n_clicks > 0:
            ridge_statistics.ridge_statistics(years_locs_dict=years_locs, saveAsJson=True, run_as_app=True)
            print('Simulation has been run. Check the console for output.')
            json_data = {}
            for season in years_locs.keys():
                year = season.split('-')[0] # get the year, which is the first part of the season
                json_data[season] = {}
                for location in years_locs[season]:
                    with open(os.path.join(constants.pathName_dataResults, 'ridge_statistics', f"ridge_statistics_{year}{location}.json"), 'r') as f:
                        json_data[season][location] = json.load(f)
            return 'Simulation has been run. Check the console for output.', json_data
        return '', {}
    


    

    @app.callback(
        Output('confirm', 'message', allow_duplicate=True),
        Output('confirm', 'displayed', allow_duplicate=True),
        Input('show-ridge-data-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_extracted_data(n_clicks):
        if n_clicks:
            return helping_functions.find_data_in_folder(os.path.join(constants.pathName_dataResults, 'ridge_statistics'))
        return "", False