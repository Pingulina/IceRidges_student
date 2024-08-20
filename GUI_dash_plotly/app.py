# this is the main file of the GUI
# the GUI is realized as dash application using dash and plotly
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, dash_table
import plotly.graph_objs as go
import pandas as pd
import os
import sys
import json
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


### load the needed variables from other files
# get the possible years for the simulation
# Load the JSON data from mooring_locations.json
data_folder = os.path.join(os.getcwd(), 'Data')
json_file_path = os.path.join(data_folder, 'mooring_locations.json')

with open(json_file_path, 'r') as file:
    mooring_data = json.load(file)

# Generate the options for the dropdown of the years
year_options = [{'label': year, 'value': year} for year in mooring_data.keys()]


# # Generate the options for the checklist
# year_options = []
# for year, locations in mooring_data.items():
#     year_options.append(
#     html.Div([
#         html.Label(year, style={'margin-right': '10px'}),
#         dcc.Checklist(
#             options=[[{'label': location, 'value': f"{year}-{location}"} for location in locations] for year, locations in mooring_data.items()],
#             value=[],  # No checkboxes marked initially
#             labelStyle={'display': 'inline-block', 'margin-right': '10px'}
#         )
#     ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'}
#     ))

# year_options = html.Div(year_options, id='year-location-selection-checklist')

# for year, locations in mooring_data.items():
#     year_options.append({'label': location, 'value': f"{year}-{location}"} for location in locations)


### Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True) # suppress_callback_exceptions=True is needed to suppress the error message when clicking on the tabs

### Define the layout of the app
app.layout = html.Div([
    dcc.Tabs(id="tabs-all", value='tab-1', children=[
        dcc.Tab(label='Tab 1 - Settings', value='tab-1'),
        dcc.Tab(label='Tab 2 - Simulation', value='tab-2'),
        dcc.Tab(label='Tab 3 - Vizualization', value='tab-3'),
    ]),
    html.Div(id='tabs-content'), # this is where the content of the tabs will be rendered
    html.Div(id='selected-values-display'),
    dcc.Store(id='selected-years-locations-store', storage_type='local'), # store component to hold the selected years and locations
    dcc.Store(id='constants-store', data=constants), # store the constants in a hidden div
    dcc.Store(id='json-data-store', data=mooring_data), # store the JSON data
    dcc.Store(id='ridge_statistics-output', data={}) # store the ridge statistics output
])

### Import the callback files
from callbacks.tab1_callbacks import register_tab1_callbacks
from callbacks.tab2_callbacks import register_tab2_callbacks
from callbacks.tab3_callbacks import register_tab3_callbacks

# Register the callbacks for each tab
register_tab1_callbacks(app)
register_tab2_callbacks(app)
register_tab3_callbacks(app)

### Render the tab structure
# Callback to render the content of each tab
@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-all', 'value'),
)
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            # html.P('Select Seasons and Locations for Analysis:'),
            # # html.Div(year_options),
            # year_options,
            # html.Button('Store Selected Values', id='store-selected-years-locations-button'),
            # html.Div(id='year-options-container'),  # Placeholder for year options

            html.Div([
                html.Label('Select Year:'),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=year_options,
                    value=None,
                    placeholder="Select a year"
                ),
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'top'}),
            html.Div(
                [
                    html.Label('Select Locations:'),
                    dcc.Checklist(
                        id='location-checklist',
                        options=[],
                        value=[],
                        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                    ),
                ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}
            ),
            html.Button('Add selected year and location(s)', id='add-button', n_clicks=0, className='button-default'),
            html.Div(id='selected-values-display'),

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
                html.Button('Extract data', id='run-extract_ridge_LI_data-button', n_clicks=0, className='button-default')
            ]),
            html.Div([
                html.P('Run Simulation:'),
                html.Button('Find ridges', id='run-ridge_statistics-button', n_clicks=0, className='button-default')
            ]),
            html.Div([
                html.P('Generate Report:'),
                html.Button('Generate Report', id='generate-report-button', n_clicks=0, className='button-default')
            ]),
            html.Div(id='ridge_statistics-output'),
            dcc.Loading(
                id="loading-simulation",
                type="default",
                children=html.Div(id='simulation-progress-output')
            ),
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.P('Ridge Statistics Visualization:'),
            html.P('Select the year and location for the plot:'),
            dcc.Dropdown(
                id='season-plot-dropdown',
                placeholder="Select a season"
            ),
            dcc.Dropdown(
                id='location-plot-dropdown',
                placeholder="Select a location"
            ),
            dcc.Graph(id='plot-output'),
            html.Button('Load JSON Data', id='load-json-data-button', n_clicks=0, className='button-default'),
            html.Button('Render Plot', id='render-plot-button', n_clicks=0, className='button-default'),
        ])





### Run the app
if __name__ == '__main__':
    app.run_server(debug=True)