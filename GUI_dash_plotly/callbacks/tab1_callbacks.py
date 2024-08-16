from dash import Input, Output, State

#### Callbacks for Tab 1  
def register_tab1_callbacks(app):
    # Callback to store the selected values for years and locations  
    @app.callback(
        Output('selected-years-locations-store', 'data'),
        Input('store-selected-years-locations-button', 'n_clicks'),
        State('year-location-selection-checklist', 'value'),
        prevent_initial_call=True
    )
    def store_selected_values(n_clicks, selected_values):
        return selected_values
    
    # Callback to restore the selected values for years and locations if the tab is chosen again
    @app.callback(
        Output('year-location-selection-checklist', 'value'),
        Input('selected-years-locations-store', 'data')
    )
    def restore_selected_values(stored_values):
        if stored_values is None:
            return []
        return stored_values
    
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