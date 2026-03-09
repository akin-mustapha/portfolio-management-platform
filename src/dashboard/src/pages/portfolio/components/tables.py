import dash_ag_grid as dag
import pandas as pd


def asset_table(data=None):

    if data is None:
        return dag.AgGrid()

    df = pd.DataFrame(data)

    # precision control
    decimals = 6
    df["pct_drawdown"] = df["pct_drawdown"].round(decimals)
    df["volatility_30d"] = df["volatility_30d"].round(decimals)
    df["volatility_50d"] = df["volatility_50d"].round(decimals)
    df["recent_profit_low_30d"] = df["recent_profit_low_30d"].round(decimals)
    df["recent_profit_high_30d"] = df["recent_profit_high_30d"].round(decimals)
    # df["price_vs_ma_50"] = df["price_vs_ma_50"].round(decimals)
    df["dca_bias"] = df["dca_bias"].round(decimals)

    return dag.AgGrid(
        rowData=df.to_dict("records"),
        columnDefs=[
            {
                "field": "ticker",
                "headerTooltip": "Asset name or ticker symbol."
            },
            {
                "field": "name",
                "headerTooltip": "Brief description of the asset. Context only — not a trading signal."
            },
            {
                "field": "value",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": "Current total value of your position (price × quantity)."
            },
            {
                "field": "profit",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": (
                    "Unrealised profit or loss. "
                    "Green means you’re up, red means drawdown. "
                    "Use alongside drawdown and volatility."
                ),
                "cellStyle": {
                    "styleConditions": [
                        {"condition": "params.value > 0", "style": {"color": "green"}},
                        {"condition": "params.value < 0", "style": {"color": "red"}},
                    ]
                },
            },
            {
                "field": "price",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": "Latest market price of the asset."
            },
            {
                "field": "recent_profit_high_30d",
                "headerName": "30D High",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": (
                    "Highest price reached in the last 30 days. "
                    "Use to judge how far price has pulled back."
                ),
            },
            {
                "field": "recent_profit_low_30d",
                "headerName": "30D Low",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": (
                    "Lowest price in the last 30 days. "
                    "Helps frame downside risk and recent range."
                ),
            },
            {
                "field": "pct_drawdown",
                "headerName": "% Drawdown",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
                "headerTooltip": (
                    "Percentage decline from the recent high. "
                    "More negative = deeper drawdown."
                ),
                "cellStyle": {
                    "styleConditions": [
                        {"condition": "params.value > 0", "style": {"color": "green"}},
                        {"condition": "params.value < 0", "style": {"color": "red"}},
                    ]
                },
            },
            {
                "field": "volatility_30d",
                "headerName": "Volatility 30D",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
                "headerTooltip": (
                    "30-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": {
                    "styleConditions": [
                        {"condition": "params.value > 0", "style": {"color": "green"}},
                        {"condition": "params.value < 0", "style": {"color": "red"}},
                    ]
                },
            },
            {
                "field": "volatility_50d",
                "headerName": "Volatility 50D",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
                "headerTooltip": (
                    "50-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": {
                    "styleConditions": [
                        {"condition": "params.value > 0", "style": {"color": "green"}},
                        {"condition": "params.value < 0", "style": {"color": "red"}},
                    ]
                },
            },
            {
                "field": "dca_bias",
                "headerName": "DCA Bias",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.4f')(params.value)"},
                "headerTooltip": (
                    "Dollar-Cost Averaging bias score. "
                    "Higher values suggest better conditions to average in."
                ),
                "cellStyle": {
                    "styleConditions": [
                        {"condition": "params.value > 0", "style": {"color": "green"}},
                        {"condition": "params.value < 0", "style": {"color": "red"}},
                    ]
                },
            },
            {
                "field": "data_date",
                "headerName": "Date",
                "headerTooltip": "Date this data snapshot was generated."
            },
        ],
        columnSize="responsiveSizeToFit",
        dashGridOptions={
            "rowSelection": {"mode": "multiRow"},
            "tooltipInteraction": True,
            "suppressBrowserTooltip": True,
            "theme": {
                "function": "themeBalham.withParams({ accentColor: 'blue', spacing: 4 })"
            },
        },
    )