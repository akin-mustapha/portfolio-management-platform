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
                "minWidth": 70, "width": 70,
                "headerTooltip": "Asset name or ticker symbol."
            },
            {
                "field": "name",
                "minWidth": 100, "width": 130,
                "headerTooltip": "Brief description of the asset. Context only — not a trading signal."
            },
            {
                "field": "value",
                "minWidth": 90, "width": 90,
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": "Current total value of your position (price × quantity)."
            },
            {
                "field": "profit",
                "minWidth": 80, "width": 80,
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
                "minWidth": 80, "width": 80,
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": "Latest market price of the asset."
            },
            {
                "field": "recent_profit_high_30d",
                "headerName": "30D High",
                "minWidth": 88, "width": 88,
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
                "minWidth": 88, "width": 88,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.2f’)(params.value)"},
                "headerTooltip": (
                    "Lowest price in the last 30 days. "
                    "Helps frame downside risk and recent range."
                ),
            },
            {
                "field": "pct_drawdown",
                "headerName": "% DD",
                "minWidth": 72, "width": 72,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘.2%’)(params.value)"},
                "headerTooltip": (
                    "% Drawdown: Percentage decline from the recent high. "
                    "More negative = deeper drawdown."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "volatility_30d",
                "headerName": "Vol 30D",
                "minWidth": 80, "width": 80,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.4f’)(params.value)"},
                "headerTooltip": (
                    "Volatility 30D: 30-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "volatility_50d",
                "headerName": "Vol 50D",
                "minWidth": 80, "width": 80,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(‘,.4f’)(params.value)"},
                "headerTooltip": (
                    "Volatility 50D: 50-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "dca_bias",
                "headerName": "DCA Bias",
                "minWidth": 84, "width": 84,
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
                "minWidth": 100, "width": 100,
                "valueFormatter": {"function": "params.value ? new Date(params.value).toLocaleDateString(‘en-GB’, {year: ‘numeric’, month: ‘short’, day: ‘numeric’}) : ‘’"},
                "headerTooltip": "Date this data snapshot was generated."
            },
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "cellStyle": {"display": "flex", "alignItems": "center"},
        },
        columnSize="autoSize",
        dashGridOptions={
            "rowSelection": {"mode": "singleRow"},
            "selectionColumnDef": {"width": 36, "minWidth": 36, "maxWidth": 36},
            "tooltipInteraction": True,
            "enableBrowserTooltips": False,
            "rowBuffer": 10,
            "rowHeight": 32,
            "headerHeight": 36,
        },
        style={"height": "100%"},
    )