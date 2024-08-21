from dash import Input, Output, State, dcc, html
import os
import sys

### import_module.py is a helper function to import modules from different directories, it is located in the base directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from import_module import import_module
constants = import_module('constants', 'helper_functions')


#### Callbacks for Tab 1  
def register_tab1_callbacks(app):
    # Callback to update the location checklist
    @app.callback(
        Output('location-checklist', 'options'),
        Output('location-checklist', 'value'),
        [Input('year-dropdown', 'value')],
        [State('json-data-store', 'data'),
         State('selected-years-locations-store', 'data')]
    )
    def update_location_checklist(selected_year, mooring_data, current_data):
        if selected_year:
            if selected_year in current_data:
                selected_locations = [f"{selected_year}-{location}" for location in current_data[selected_year]]
            else:
                selected_locations = []
            return [{'label': location, 'value': f"{selected_year}-{location}"} for location in mooring_data[selected_year]], selected_locations
        return [],[]

    # Callback to update the selected values
    @app.callback(
        Output('selected-years-locations-store', 'data'),
        [Input('add-button-yearLoc', 'n_clicks')],
        [State('year-dropdown', 'value'),
        State('location-checklist', 'value'),
        State('selected-years-locations-store', 'data')],
        prevent_initial_call=True,
    )
    def update_selected_values(n_clicks, selected_year, selected_locations, current_data):
        if n_clicks > 0 and selected_year and selected_locations:
            print(f"n_clicks: {n_clicks}")
            print(f"current_data: {current_data}")
            print(f"selected_year: {selected_year}")
            print(f"selected_locations: {selected_locations}")
            if n_clicks == 1 and current_data is None:
                current_data = {}
            
            current_data[selected_year] = [loc[10:] for loc in selected_locations if loc[0:9] == selected_year]
            # Remove duplicates
            current_data[selected_year] = list(set(current_data[selected_year]))
            # sort by location
            current_data[selected_year].sort()
            # sort by year (key)
            current_data = dict(sorted(current_data.items()))
            # Remove key, if the list is empty
            if not current_data[selected_year]:
                del current_data[selected_year]
            display_list = [html.Li(f"Year: {year}, Locations: {', '.join(locations)}") for year, locations in current_data.items()]
            return current_data # Return the updated current data
        return current_data # Return the current data if no new values are added
    
    # Callback to display the selected values
    @app.callback(
        Output('selected-values-display', 'children'), 
        Input('tabs-all', 'value'),
        Input('selected-years-locations-store', 'data'),
        prevent_initial_call=True
    )
    def display_selected_values(tab, current_data):
        if tab == 'tab-1':
            display_list = [html.Li(f"Year: {year}, Locations: {', '.join(locations)}") for year, locations in current_data.items()]
            return html.Ul(display_list)
        return html.Ul()
    
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
            # save the new constants to the global variable constants
            for key, value in stored_constants.items():
                constants[key] = value
        return stored_constants