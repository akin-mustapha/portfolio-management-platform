import dash_ag_grid as dag

def asset_table(df):
  return dag.AgGrid(
    rowData=df.to_dict("records"),
    columnDefs=[
        {"field": "name"},
        {"field": "description"},
        {
            "field": "profit",
            "type": "numericColumn",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
            "cellStyle": {
                "styleConditions": [
                    {
                        "condition": "params.value > 0",
                        "style": {"color": "green"}
                    },
                    {
                        "condition": "params.value < 0",
                        "style": {"color": "red"}
                    }
                ]
            }
        },
        {
            "field": "price",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
        },
        {
            "field": "value",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
        }
    ],
    # style={"height": "100%"},
  )