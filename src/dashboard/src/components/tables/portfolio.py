import dash_ag_grid as dag

def portfolio_timeseries_table(df):
  return dag.AgGrid(
    rowData=df.to_dict("records"),
    columnDefs=[
    {"field": "data_date"},
    {"field": "portfolio_value"},
    {
      "field": "unrealized_return",
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
    }
    ],
    # style={"height": "100%"},
  )