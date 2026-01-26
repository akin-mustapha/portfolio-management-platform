import dash_ag_grid as dag
from src.dashboard.src.components.tables.table import create_table

def asset_table(df):
  decimals = 4
  df['pct_drawdown'] = df['pct_drawdown'].round(decimals=decimals)
  df['volatility_30d'] = df['volatility_30d'].round(decimals=decimals)
  df['price_vs_ma_50'] = df['price_vs_ma_50'].round(decimals=decimals)
  df['dca_bias'] = df['dca_bias'].round(decimals=decimals)
  return create_table("asset_table", df.columns, df.to_dict("records"))
  return dag.AgGrid(
    rowData=df.to_dict("records"),
    columnDefs=[
        {"field": "name"},
        {"field": "description"},
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
            "field": "volatility_30d",
            "type":"numericColumn",
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
            "field": "price_vs_ma_50",
            "type":"numericColumn",
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
            "field": "dca_bias",
            "type":"numericColumn",
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