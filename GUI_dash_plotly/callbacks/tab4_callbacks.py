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
level_ice_statistics_plotly = import_module('level_ice_statistics_plotly', 'plot_functions')
simulation_ridges_plotly = import_module('simulation_ridges_plotly', 'simulation_functions')
simulation_consolidated_layer = import_module('simulation_consolidated_layer', 'simulation_functions')

def register_tab4_callbacks(app):
    # here comes the callback for the load simulations
    @app.callback(
        Output('load-simplified-plot', 'figure'),
        Input('load-simulations-button', 'n_clicks'),
        State('diameter-structure', 'value'),
        State('years-simulation-load', 'value'),
        
    )
    def load_simulations(n_clicks, w, years=1000):
        if n_clicks:
            print('Loading simulations')
            water_depth = 20
            hmu = 1.8
            wn = 40
            R, Hi, Hc_vec, Tw, Hw, Fam, Fam_sorted, Y_sorted, CRam, shape, loc, scale = simulation_consolidated_layer.consolidated_layer_simulation(w, water_depth, hmu, wn, years)
            fig = simulation_consolidated_layer.consolidated_layer_plot(R, Hi, Hc_vec, Tw, Hw, Fam, Fam_sorted, Y_sorted, CRam, shape, loc, scale)
            return fig
        return go.Figure()   
        # return None, None, None, None, None