import dash_ag_grid as dag
def asset_table(data=None):

  if data is None:
    return dag.AgGrid()
  # TODO: CREATE ENUM TO HOLD CONSTANT VALUES.
  decimals = 6
  data['pct_drawdown'] = data['pct_drawdown'].round(decimals=decimals)
  data['volatility_30d'] = data['volatility_30d'].round(decimals=decimals)
  data['price_vs_ma_50'] = data['price_vs_ma_50'].round(decimals=decimals)
  data['dca_bias'] = data['dca_bias'].round(decimals=decimals)
  return dag.AgGrid(
    rowData=data.to_dict("records"),
    columnDefs=[
        {"field": "name"},
        {"field": "asset_description"},
        {"field": "data_date"},
        {
            "field": "value",
            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
        },
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
            "field": "recent_high_30d",
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
            "field": "recent_low_30d",
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
            "field": "pct_drawdown",
            "type":"numericColumn",
            "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
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
            "field": "volatility_30d",
            "type":"numericColumn",
            "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
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
            "field": "price_vs_ma_50",
            "type":"numericColumn",
            "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
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
            "field": "dca_bias",
            "type":"numericColumn",
            "valueFormatter": {"function": "d3.format('.4f')(params.value)"},
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
    ]
  )