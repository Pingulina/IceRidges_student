# this is the main file of the GUI
# the GUI is realized as dash application using dash and plotly
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import dash_table
import pandas as pd
import os
import sys

import example_simulation
### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants_original = import_module('constants_original', 'helper_functions')
constants = import_module('constants', 'helper_functions')

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
            html.Button('Run Simulation', id='run-simulation-button', n_clicks=0),
            html.Div(id='simulation-output')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.P('This tab will be filled later.')
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

# @app.callback(
#     Output('tabs-content-example', 'children'),
#     Input('update-button', 'n_clicks'),
#     State('table', 'data'),
#     prevent_initial_call=True
# )
# def update_constants(n_clicks, rows):
#     if n_clicks > 0:
#         for row in rows:
#             constants[row['Parameter']] = row['New Value']
#     return render_content('tab-1')

### Callbacks for Tab 2
# Callback to handle the button click in Tab 2
@app.callback(
    Output('simulation-output', 'children'),
    Input('run-simulation-button', 'n_clicks')
)
def run_simulation(n_clicks):
    if n_clicks > 0:
        example_simulation.run_simulation()
        return 'Simulation has been run. Check the console for output.'
    return ''

### Callbacks for Tab 3
# here come the callbacks for the visualization tab

### Run the app
if __name__ == '__main__':
    app.run_server(debug=True)