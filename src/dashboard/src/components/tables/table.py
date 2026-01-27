from dash import dash_table

def create_table(id, columns, data, page_size=20, editable=False, filter_action="native"):
    return dash_table.DataTable(
        id=id,
        columns=[{"name": col, "id": col} for col in columns],
        data=data,
        page_size=page_size,
        editable=editable,
        filter_action=filter_action,  # allows user-side filtering
        sort_action="native",
        sort_mode="multi",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#232426",
            "fontWeight": "thin",
            "fontSize": 13,
            'color': "#DCE0E7",
        },
        style_cell={
            "textAlign": "left",
            "padding": "8px",
            "minWidth": "80px", "width": "120px", "maxWidth": "200px",
            'color': '#232426',
            "fontSize": 12,


        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#232426',
                'color': "#DCE0E7",
            }
     
        ],
    )