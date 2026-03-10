import dash_bootstrap_components as dbc
from dash import html


PALETTE = {
    "positive": "#26a69a",   # teal green
    "neutral":  "#9ca3af",   # slate gray
    "warning":  "#B08900",   # soft amber
    "risk":     "#ef5350",   # red
}


def _fmt_pct(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}%"


def _dark_kpi_card(label, value_str, unit="", change_str="", change_color=None):
    if change_color is None:
        change_color = PALETTE["neutral"]
    return html.Div([
        html.Div(label, className="kpi-label"),
        html.Div([
            html.Div([
                html.Span(value_str, className="kpi-value"),
                html.Span(unit, className="kpi-unit") if unit else None,
            ], className="d-flex align-items-baseline"),
            html.Span(change_str, className="kpi-change", style={"color": change_color}) if change_str else None,
        ], className="d-flex align-items-baseline justify-content-between"),
    ], className="kpi-card")


def kpi_color(value, kind):
    if kind == "drawdown":
        if value <= -8:
            return PALETTE["risk"]
        elif value <= -4:
            return PALETTE["warning"]
        else:
            return PALETTE["neutral"]

    if kind == "trend":
        return PALETTE["positive"] if value == "Bullish" else PALETTE["neutral"]

    if kind == "volatility":
        if value >= 0.04:
            return PALETTE["risk"]
        elif value >= 0.02:
            return PALETTE["warning"]
        else:
            return PALETTE["neutral"]

    if kind == "dca":
        return PALETTE["positive"] if value > 0 else PALETTE["neutral"]

    return PALETTE["neutral"]


def asset_kpi_row(df):
    return dbc.Row(
        [
            dbc.Col(_dark_kpi_card("Total Assets", str(len(df)))),
            dbc.Col(_dark_kpi_card("Average Price", f"${df['price'].mean().round(decimals=2):,.2f}", unit="USD")),
            dbc.Col(_dark_kpi_card("Volatility", f"{df['volatility_30d'].mean().round(decimals=4):.4f}")),
        ],
        className="mb-4 g-3"
    )


def asset_kpi_section(data):
    if isinstance(data, list):
        data = data[-1]

    price: float = data.get("price", 0)
    drawdown: float = data.get("pct_drawdown", 0)
    trend: str = data.get("trend", "")
    volatility: float = data.get("volatility_30d", 0)
    dca_bias: float = data.get("dca_bias", 0)

    price_fmt      = f"${price:,.2f}"
    drawdown_fmt   = _fmt_pct(drawdown)
    volatility_fmt = f"{volatility:.4f}"
    dca_bias_fmt   = f"{dca_bias:.4f}"

    return dbc.Row([
        dbc.Col(_dark_kpi_card("Price", price_fmt, unit="USD")),
        dbc.Col(_dark_kpi_card(
            "30D Drawdown", drawdown_fmt,
            change_color=kpi_color(drawdown, "drawdown"),
        )),
        dbc.Col(_dark_kpi_card(
            "Trend", trend,
            change_color=kpi_color(trend, "trend"),
        )),
        dbc.Col(_dark_kpi_card(
            "Volatility (30D)", volatility_fmt,
            change_color=kpi_color(volatility, "volatility"),
        )),
        dbc.Col(_dark_kpi_card(
            "DCA Bias", dca_bias_fmt,
            change_color=kpi_color(dca_bias, "dca"),
        )),
    ], className="mb-4 g-3 row-cols-2 row-cols-md-5")


def asset_kpi_section_empty():
    return dbc.Row([
        dbc.Col(_dark_kpi_card("Price", "—", unit="USD")),
        dbc.Col(_dark_kpi_card("30D Drawdown", "—")),
        dbc.Col(_dark_kpi_card("Trend", "—")),
        dbc.Col(_dark_kpi_card("Volatility (30D)", "—")),
        dbc.Col(_dark_kpi_card("DCA Bias", "—")),
    ], className="mb-4 g-3 row-cols-2 row-cols-md-5")
