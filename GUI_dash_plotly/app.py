# this is the main file of the GUI
# the GUI is realized as dash application using dash and plotly
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import dash_table
import plotly.graph_objs as go
import pandas as pd
import os
import sys
import json

import example_simulation
### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants_original = import_module('constants_original', 'helper_functions')
constants = import_module('constants', 'helper_functions')
extract_ridge_LI_data = import_module('extract_ridge_LI_data', 'initialization_preparation')
ridge_statistics = import_module('ridge_statistics', 'data_analysis')
ridge_statistics_plot_plotly = import_module('ridge_statistics_plot_plotly', 'plot_functions')

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True) # suppress_callback_exceptions=True is needed to suppress the error message when clicking on the tabs

# Define the layout of the app
app.layout = html.Div([
    dcc.Tabs(id="tabs-example", value='tab-1', children=[
        dcc.Tab(label='Tab 1 - Settings', value='tab-1'),
        dcc.Tab(label='Tab 2 - Simulation', value='tab-2'),
        dcc.Tab(label='Tab 3 - Vizualization', value='tab-3'),
    ]),
    html.Div(id='tabs-content-example'), # this is where the content of the tabs will be rendered
    dcc.Store(id='constants-store', data=constants), # store the constants in a hidden div
    dcc.Store(id='json-store'), # store the JSON data
])

# Callback to render the content of each tab
@app.callback(
    Output('tabs-content-example', 'children'),
    Input('tabs-example', 'value')
)

def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            dash_table.DataTable(
                id='table',
                columns=[
                    {"name": "Parameter", "id": "Parameter"},
                    {"name": "Value", "id": "Value"},
                    {"name": "New Value", "id": "New Value", "editable": True}
                ],
                data = [{"Parameter": key, "Value": value, "New Value": value} for key, value in constants_original.items()],
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {
                            'filter_query': '{New Value} != {Value}',
                            'column_id': 'New Value'
                        },
                        'color': 'red'
                    },
                    {
                        'if': {
                            'filter_query': '{New Value} = {Value}',
                            'column_id': 'New Value'
                        },
                        'color': 'gray'
                    }
                ]
            ),
            html.Button('Update Constants', id='update-button', n_clicks=0)
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                html.P('Extract data:'),
                html.Button('Extract data', id='run-extract_ridge_LI_data-button', n_clicks=0)
            ]),
            html.Div([
                html.P('Run Simulation:'),
                html.Button('Find ridges', id='run-ridge_statistics-button', n_clicks=0)
            ]),
            html.Div([
                html.P('Generate Report:'),
                html.Button('Generate Report', id='generate-report-button', n_clicks=0)
            ]),
            html.Div(id='simulation-output')
        ])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Graph(id='plot-output')
        ])

#### Callbacks for Tab 1    
# Callback to update the table data
@app.callback(
    Output('table', 'data'),
    Input('table', 'data_timestamp'),
    Input('table', 'data')
)
def update_table_data(timestamp, rows):
    return rows

# Callback to update the constants
@app.callback(
    Output('constants-store', 'data'),
    Input('update-button', 'n_clicks'),
    State('table', 'data'),
    State('constants-store', 'data'),
    prevent_initial_call=True
)
def update_constants(n_clicks, rows, stored_constants):
    if n_clicks > 0:
        for row in rows:
            stored_constants[row['Parameter']] = row['New Value']
        print(stored_constants)
    return stored_constants


### Callbacks for Tab 2
# Callback to handle the button click for extract ridge levelIce data in Tab 2
@app.callback(
    Output('simulation-output', 'children', allow_duplicate=True),
    Input('run-extract_ridge_LI_data-button', 'n_clicks'),
    prevent_initial_call=True
)
def run_extract_ridge_LI_data(n_clicks):
    if n_clicks > 0:
        extract_ridge_LI_data.extract_ridge_LI_data(terminal_use=False, change_seasons=['2004-2005'], new_locations=['a', 'b'], overwrite=True, use_existing_mooringLocs=True)
        return 'Simulation has been run. Check the console for output.'
    return ''

# Callback to handle the button click for ridge statistics in Tab 2
@app.callback(
    Output('simulation-output', 'children', allow_duplicate=True),
    Input('run-ridge_statistics-button', 'n_clicks'),
    prevent_initial_call=True
)
def run_ridge_statistics(n_clicks):
    if n_clicks > 0:
        ridge_statistics.ridge_statistics(years=[2004], poss_mooring_locs=['a'], saveAsJson=True, run_as_app=True)
        with open(os.path.join(constants.pathName_dataResults, 'ridge_statistics', f"ridge_statistics_{2004}{'a'}.json"), 'r') as f:
            json_data = json.load(f)
        return 'Simulation has been run. Check the console for output.', json_data
    return '', {}

### Callbacks for Tab 3
# here come the callbacks for the visualization tab
# Callback to update the plot for ridge statistics
@app.callback(
    Output('plot-output', 'figure'),
    Input('plot-store', 'data')
)
def update_plot(json_data):
    if json_data:
        fig = ridge_statistics_plot_plotly.plot_per_location(json_data, year=2004, loc='a')
        return fig
    return go.Figure()

### Run the app
if __name__ == '__main__':
    app.run_server(debug=True)