"""Organism — AG Grid asset table (the main portfolio data grid)."""

import dash_ag_grid as dag
import pandas as pd
from dash import html

from ...charts.chart_theme import POSITIVE_COLOR, NEGATIVE_COLOR


def asset_table(data=None):

    if data is None:
        return html.Div()

    df = pd.DataFrame(data)

    # PostgreSQL NUMERIC columns come back as Python Decimal objects (object dtype).
    # Convert all numeric columns to float before any arithmetic to avoid
    # "Expected numeric dtype, got object instead" in pandas 2.0+.
    numeric_cols = [
        "value",
        "profit",
        "price",
        "avg_price",
        "cost",
        "weight_pct",
        "pnl_pct",
        "value_drawdown_pct_30d",
        "volatility_30d",
        "volatility_50d",
        "value_ma_30d",
        "value_ma_50d",
        "dca_bias",
        "recent_profit_high_30d",
        "recent_profit_low_30d",
        "var_95_1d",
        "cumulative_value_return",
        "daily_value_return",
        "fx_impact",
        "value_ma_crossover_signal",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # precision control
    decimals = 6
    df["weight_pct"] = df["weight_pct"].round(decimals)
    df["value_drawdown_pct_30d"] = df["value_drawdown_pct_30d"].round(decimals)
    df["volatility_30d"] = df["volatility_30d"].round(decimals)
    df["recent_profit_high_30d"] = df["recent_profit_high_30d"].round(decimals)
    df["dca_bias"] = df["dca_bias"].round(decimals)
    df["pnl_pct"] = df["pnl_pct"].round(decimals)
    df["avg_price"] = df["avg_price"].round(decimals)
    if "var_95_1d" in df.columns:
        df["var_95_1d"] = df["var_95_1d"].round(decimals)
    if "cumulative_value_return" in df.columns:
        df["cumulative_value_return"] = df["cumulative_value_return"].round(decimals)
    if "daily_value_return" in df.columns:
        df["daily_value_return"] = df["daily_value_return"].round(decimals)

    def pnl_style(positive_color=POSITIVE_COLOR, negative_color=NEGATIVE_COLOR):
        return {
            "styleConditions": [
                {
                    "condition": "params.value > 0",
                    "style": {"color": positive_color, "fontWeight": "600"},
                },
                {
                    "condition": "params.value < 0",
                    "style": {"color": negative_color, "fontWeight": "600"},
                },
            ]
        }

    return dag.AgGrid(
        id="portfolio-asset-table",
        className="finance-grid",
        rowData=df.to_dict("records"),
        columnDefs=[
            {
                "field": "trend",
                "pinned": "left",
                "suppressMovable": True,
                "minWidth": 116,
                "width": 116,
                "cellRenderer": "TrendSparkline",
                "cellStyle": {"padding": "0", "overflow": "hidden"},
                "headerTooltip": "30-day price trend. Green = Bullish (MA30 > MA50), Red = Bearish.",
            },
            {
                "field": "ticker",
                "headerName": "Ticker",
                "pinned": "left",
                "suppressMovable": True,
                "minWidth": 70,
                "width": 70,
                "headerTooltip": "Asset name or ticker symbol.",
            },
            {
                "field": "name",
                "minWidth": 100,
                "width": 130,
                "tooltipField": "name",
                "headerTooltip": "Brief description of the asset. Context only — not a trading signal.",
            },
            {
                "field": "value",
                "headerName": "Value",
                "minWidth": 90,
                "width": 90,
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": "Current total value of your position (price × quantity).",
            },
            {
                "field": "profit",
                "headerName": "P&L",
                "minWidth": 80,
                "width": 80,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": (
                    "Unrealised profit or loss. "
                    "Green means you're up, red means drawdown. "
                    "Use alongside drawdown and volatility."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "pnl_pct",
                "headerName": "P&L %",
                "minWidth": 80,
                "width": 80,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.2%')(params.value)"},
                "headerTooltip": "Unrealised P&L as a percentage of cost basis. Comparable across positions.",
                "cellStyle": pnl_style(),
            },
            {
                "field": "cumulative_value_return",
                "headerName": "Cumul. Return",
                "minWidth": 108,
                "width": 108,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.2%')(params.value)"},
                "headerTooltip": "Total return % since position opened.",
                "cellStyle": pnl_style(),
            },
            {
                "field": "daily_value_return",
                "headerName": "Daily Return",
                "minWidth": 96,
                "width": 96,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.2%')(params.value)"},
                "headerTooltip": "Single-day % price change.",
                "cellStyle": pnl_style(),
            },
            {
                "field": "value_ma_crossover_signal",
                "headerName": "MA Signal",
                "minWidth": 94,
                "width": 94,
                "valueFormatter": {
                    "function": "params.value == null ? '—' : params.value > 0 ? '↑ Bullish' : '↓ Bearish'"
                },
                "cellStyle": pnl_style(),
                "headerTooltip": "MA crossover signal. ↑ Bullish = MA20 above MA50 (short-term uptrend). ↓ Bearish = MA20 below MA50.",
            },
            {
                "field": "price",
                "headerName": "Price",
                "minWidth": 80,
                "width": 80,
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": "Latest market price of the asset.",
            },
            {
                "field": "avg_price",
                "headerName": "Avg Cost",
                "minWidth": 84,
                "width": 84,
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": "Average price paid (DCA average). Compare against current price to understand DCA Bias.",
            },
            {
                "field": "weight_pct",
                "headerName": "Weight %",
                "minWidth": 84,
                "width": 84,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.2%')(params.value)"},
                "headerTooltip": "Weight in relation to portfolio value",
            },
            {
                "field": "recent_profit_high_30d",
                "headerName": "30D High",
                "minWidth": 88,
                "width": 88,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": (
                    "Highest price reached in the last 30 days. "
                    "Use to judge how far price has pulled back."
                ),
            },
            {
                "field": "value_drawdown_pct_30d",
                "headerName": "% DD",
                "minWidth": 72,
                "width": 72,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.2%')(params.value)"},
                "headerTooltip": (
                    "% Drawdown: Percentage decline from the recent high. "
                    "More negative = deeper drawdown."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "volatility_30d",
                "headerName": "Vol 30D",
                "minWidth": 80,
                "width": 80,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.4f')(params.value)"},
                "headerTooltip": (
                    "Volatility 30D: 30-day volatility measure. "
                    "Higher values indicate larger price swings."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "var_95_1d",
                "headerName": "VaR 95%",
                "minWidth": 84,
                "width": 84,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                "headerTooltip": "Value at Risk (95% confidence, 1-day). Maximum expected daily loss under normal conditions.",
                "cellStyle": pnl_style(),
            },
            {
                "field": "dca_bias",
                "headerName": "DCA Bias",
                "minWidth": 84,
                "width": 84,
                "type": "numericColumn",
                "valueFormatter": {"function": "d3.format('.4f')(params.value)"},
                "headerTooltip": (
                    "Dollar-Cost Averaging bias score. "
                    "Higher values suggest better conditions to average in."
                ),
                "cellStyle": pnl_style(),
            },
            {
                "field": "data_date",
                "headerName": "Date",
                "minWidth": 100,
                "width": 100,
                "valueFormatter": {
                    "function": "params.value ? new Date(params.value).toLocaleDateString('en-GB', {year: 'numeric', month: 'short', day: 'numeric'}) : ''"
                },
                "headerTooltip": "Date this data snapshot was generated.",
            },
        ],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "cellStyle": {"display": "flex", "alignItems": "center"},
        },
        columnSize="autoSize",
        dashGridOptions={
            "rowSelection": {
                "mode": "multiRow",
                "maxSelectedRows": 3,
                "enableSelectionWithoutKeys": True,
            },
            "selectionColumnDef": {"width": 36, "minWidth": 36, "maxWidth": 36},
            "tooltipInteraction": True,
            "enableBrowserTooltips": False,
            "rowBuffer": 10,
            "rowHeight": 32,
            "headerHeight": 36,
            "unSortIcon": True,
        },
        style={"height": "100%"},
    )
