# this is the main file of the GUI
# the GUI is realized as dash application using dash and plotly
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.io as pio
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

### Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.YETI]) # suppress_callback_exceptions=True is needed to suppress the error message when clicking on the tabs

### Define the layout of the app
app.layout = html.Div([
    dcc.Tabs(id="tabs-all", value='tab-1', children=[
        dcc.Tab(label='Tab 1 - Settings', value='tab-1'),
        dcc.Tab(label='Tab 2 - Simulation', value='tab-2'),
        dcc.Tab(label='Tab 3 - Vizualization', value='tab-3'),
    ]),
    html.Div(id='tabs-content'), # this is where the content of the tabs will be rendered
    html.Div(id='selected-values-display'),
    dcc.Store(id='selected-years-locations-store', data={}), # , storage_type='local' # store component to hold the selected years and locations; initialized as empty dictionary
    dcc.Store(id='constants-store', data=constants), # store the constants in a hidden div
    dcc.ConfirmDialog(
        id='confirm',
        message='',
    ), # confirm dialog to show the extracted data
    dcc.Store(id='json-data-store', data=mooring_data), # store the JSON data
    dcc.Store(id='json-data-allRidges_allYears-store', data={}), # store the JSON data for all ridges from all years and locations
    dcc.Store(id='ridge_statistics-output', data={}), # store the ridge statistics output
    dcc.Store(id='plot-json-ridges-store', data=go.Figure().to_json()), # store the plot data for the ridges
    dcc.Store(id='json-trace-indices-store', data={}), # store the trace indices for the plot data (needed for updating the plot)
    dcc.Store(id='this-time-draft-tuple', data=(0, 0)), # store the time and draft data for the current week
    dcc.Store(id='click-data-draft-index', data=None), # store the index of the clicked data point
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
    State('plot-json-ridges-store', 'data'),
)
def render_content(tab, fig_json_ridges):
    colors = {
        'background': 'rgba(255, 255, 255, 1)',
        'text': 'rgba(200, 0, 0, 1)'
    }
    if tab == 'tab-1':
        return html.Div([
            html.Div([
                html.Label('Select Season:'),
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
            html.Button('Add selected year and location(s)', id='add-button-yearLoc', n_clicks=0, className='button-default'),
            # html.Button('Reset selected year(s) and location(s)', id='reset-button-yearLoc', n_clicks=0, className='button-default'),
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
                html.P('Convert dat data to json data (might take up to 10 minutes or more per location and year):'),
                html.Button('Convert dat to json', id='convert-dat-to-json-button', n_clicks=0, className='button-default')
            ]),
            html.Div([
                html.P('Extract data (might take up to 10 minutes or more per location and year):'),
                html.Button('Extract data', id='run-extract_ridge_LI_data-button', n_clicks=0, className='button-default'),
                html.Button('Show extracted data', id='show-extracted-data-button', n_clicks=0, className='button-default')
            ]),
            html.Div([
                html.P('Find ridges (might take multiple minutes per location and year):'),
                html.Button('Find ridges', id='run-ridge_statistics-button', n_clicks=0, className='button-default'),
                html.Button('Show computed ridge data', id='show-ridge-data-button', n_clicks=0, className='button-default')
            ]),
            html.Div([
                html.P('Weekly visual analysis and correction:'),
                html.Button('button text', id='generate-report-button', n_clicks=0, className='button-default')
            ]),
            html.Div(id='ridge_statistics-output'),
            dcc.Loading(
                id="loading-simulation",
                type="default",
                children=html.Div(id='simulation-progress-output')
            ),
        ])
    elif tab == 'tab-3':
        # print('in tab 3')
        # if fig_json_ridges:
        #     fig_ridges = pio.from_json(fig_json_ridges)
        # else:
        #     fig_ridges = go.Figure()
        # print(f"fig_ridges: {fig_ridges}")
        return html.Div([
            # Dropdowns for the season and location
            dcc.Markdown('''
                ## Location and Season Selection
                Select a season and location to display the ridge statistics.
                This has to be done before any plots can be rendered.
                '''),
            dcc.Dropdown(
                id='season-plot-dropdown',
                placeholder="Select a season"
            ),
            dcc.Dropdown(
                id='location-plot-dropdown',
                placeholder="Select a location"
            ),
            dcc.Markdown('''
                        To load the data for the selected season and location, click the 'Load JSON Data' button. Loading the data once for all plots is sufficient.
                        
                        **Every time data is loaded, it may take up to a few minutes, depending on the size of the data set(s). So be patient, don't switch the tabs or click the buttons multiple times.**
                         '''),
            html.Button('Load JSON Data', id='load-json-data-button', n_clicks=0, className='button-default'),
            dcc.Markdown('''
                         If you want to run either weekly visual analysis or level ice analaysis, you need to load the additional data. 
                         '''),
            html.Button('Load additional data', id='load-weekly-analysis-button', n_clicks=0, className='button-default'),
            ########
             # Ridge statistics
            dcc.Markdown('''
                ## Ridge Statistics Visualization
                Click the 'Load JSON Data' button to load the data. 
                Afterwards, click the 'Render Plot' button to render the plot.
                '''),
            html.Button('Render Plot', id='render-plot-button', n_clicks=0, className='button-default'),
            dcc.Graph(id='plot-ridges'),
            ########
            # Weekly visual analysis and correction
            dcc.Markdown('''
                ## Weekly visual analysis and correction
                In the following, the ridges per week can be analyzed in relation to all other ridges from the whole dataset of all years and locations. 
                This data needs to be loaded additionally to the data loaded in the beginning. To do so, click the 'Load additional data' button at the top.
                '''),
            html.Button('Render plot', id='render-weekly-analysis-button', n_clicks=0, className='button-default'),
            # html.Button('Correct value', id='correct-value-button', n_clicks=0, className='button-default'),
            html.Button('Update', id='update-values-plot-button', n_clicks=0, className='button-default'),
            dcc.Markdown('''Select the week to analyze:'''),
            dcc.Slider(
                id='week-slider',
                min=1,
                max=52,
                step=1,
                value=1,
                marks={i: f'{i}' for i in range(1, 53)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            
            # Hidden div to trigger the modal
            html.Div(id='modal', style={'display': 'none'}),
            # Modal layout
            html.Div(
                id='modal-content',
                style={
                    'display': 'none',
                    'position': 'fixed',
                    'z-index': '1',
                    'left': '0',
                    'top': '0',
                    'width': '100%',
                    'height': '100%',
                    'overflow': 'auto',
                    'background-color': 'rgb(0,0,0)',
                    'background-color': 'rgba(0,0,0,0.4)',
                    'padding-top': '60px'
                },
                children=[
                    html.Div(
                        style={
                            'background-color': '#fefefe',
                            'margin': '5% auto',
                            'padding': '20px',
                            'border': '1px solid #888',
                            'width': '80%'
                        },
                        children=[
                            html.Label('Correct value for ice draft:'),
                            dcc.Input(id='new-y-coordinate', type='number', value='', step=0.1),
                            html.Button('Save', id='save-button', n_clicks=0),
                            html.Button('Close', id='cancel-button', n_clicks=0)
                        ]
                    )
                ]
            ),
            
            dcc.Graph(id='plot-weekly-analysis'), 
            html.Div(id='click-data-draft'),
            dcc.Markdown('''
                ## Level ice analysis
                In the following, the level ice can visually be analyzed.
            '''),  
            html.Button('Render plot', id='render-LI-analysis-button', n_clicks=0, className='button-default'),
            dcc.Markdown('''Select the week to analyze:'''),
            dcc.Slider(
                id='week-slider-LI',
                min=1,
                max=52,
                step=1,
                value=1,
                marks={i: f'{i}' for i in range(1, 53)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            dcc.Slider(
                id='day-slider-LI',
                min=1,
                max=7,
                step=1,
                value=1,
                marks={i: f'{i}' for i in range(1, 8)},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            dcc.Graph(id='plot-LI-analysis')
            
        ])





### Run the app
if __name__ == '__main__':
    app.run_server(debug=True)