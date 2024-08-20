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
    # # Callback to store the selected values for years and locations  
    # @app.callback(
    #     Output('selected-years-locations-store', 'data'),
    #     [Input('store-selected-years-locations-button', 'n_clicks'),
    #     Input('year-location-checklist', 'value')],
    #     prevent_initial_call=True
    # )
    # def store_selected_values(n_clicks, selected_values):
    #     print(f"selected_values {selected_values}, n_clicks {n_clicks}")
    #     return selected_values
    
    # # Callback to restore the selected values for years and locations if the tab is chosen again
    # @app.callback(
    #     Output('year-location-selection-checklist', 'value'),
    #     Input('tabs-all', 'value'),
    #     State('selected-years-locations-store', 'data')
    # )
    # def restore_selected_values(tab_click, stored_values):
    #     if stored_values is None:
    #         return []
    #     return stored_values

    @app.callback(
        Output('location-checklist', 'options'),
        [Input('year-dropdown', 'value')],
        [State('json-data-store', 'data')]
    )
    def update_location_checklist(selected_year, mooring_data):
        if selected_year:
            return [{'label': location, 'value': f"{selected_year}-{location}"} for location in mooring_data[selected_year]]
        return []

    @app.callback(
        Output('selected-values-display', 'children'),
        Output('selected-years-locations-store', 'data'),
        [Input('add-button', 'n_clicks')],
        [State('year-dropdown', 'value'),
        State('location-checklist', 'value'),
        State('selected-years-locations-store', 'data')]
    )
    def update_selected_values(n_clicks, selected_year, selected_locations, current_data):
        if n_clicks > 0 and selected_year and selected_locations:
            if n_clicks == 1 or current_data is None:
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
            return html.Ul(display_list), current_data # Return the list of selected values
        return html.Ul(), current_data # Return an empty list if no values are selected
    
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