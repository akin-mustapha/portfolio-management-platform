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

    POSITIVE_COLOR = "#26a69a"
    NEGATIVE_COLOR = "#ef5350"

    def pnl_style(positive_color=POSITIVE_COLOR, negative_color=NEGATIVE_COLOR):
        return {
            "styleConditions": [
                {"condition": "params.value > 0", "style": {"color": positive_color, "fontWeight": "600"}},
                {"condition": "params.value < 0", "style": {"color": negative_color, "fontWeight": "600"}},
            ]
        }

    return dag.AgGrid(
        id="portfolio-asset-table",
        className="finance-grid",
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
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": "Current total value of your position (price × quantity)."
            },
            {
                "field": "profit",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": (
                    "Unrealised profit or loss. "
                    "Green means you’re up, red means drawdown. "
                    "Use alongside drawdown and volatility."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "price",
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": "Latest market price of the asset."
            },
            {
                "field": "recent_profit_high_30d",
                "headerName": "30D High",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": (
                    "Highest price reached in the last 30 days. "
                    "Use to judge how far price has pulled back."
                ),
            },
            {
                "field": "recent_profit_low_30d",
                "headerName": "30D Low",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": (
                    "Lowest price in the last 30 days. "
                    "Helps frame downside risk and recent range."
                ),
            },
            {
                "field": "pct_drawdown",
                "headerName": "% Drawdown",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘.2%’)(params.value)"},
                "headerTooltip": (
                    "Percentage decline from the recent high. "
                    "More negative = deeper drawdown."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "volatility_30d",
                "headerName": "Volatility 30D",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.4f’)(params.value)"},
                "headerTooltip": (
                    "30-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "volatility_50d",
                "headerName": "Volatility 50D",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.4f’)(params.value)"},
                "headerTooltip": (
                    "50-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "dca_bias",
                "headerName": "DCA Bias",
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘.4f’)(params.value)"},
                "headerTooltip": (
                    "Dollar-Cost Averaging bias score. "
                    "Higher values suggest better conditions to average in."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "data_date",
                "headerName": "Date",
                "valueFormatter": {"function": "params.value ? new Date(params.value).toLocaleDateString('en-GB', {year: 'numeric', month: 'short', day: 'numeric'}) : ''"},
                "headerTooltip": "Date this data snapshot was generated."
            },
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "cellStyle": {"display": "flex", "alignItems": "center"},
        },
        columnSize="responsiveSizeToFit",
        dashGridOptions={
            "rowSelection": {"mode": "multiRow"},
            "tooltipInteraction": True,
            "enableBrowserTooltips": False,
            "rowBuffer": 10,
            "rowHeight": 32,
            "headerHeight": 36,
        },
    )