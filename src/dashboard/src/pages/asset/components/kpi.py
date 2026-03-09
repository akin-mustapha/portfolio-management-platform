import dash_bootstrap_components as dbc
from dash import html


PALETTE = {
    "positive": "#2F6F6A",   # muted teal
    "neutral":  "#6B7280",   # slate gray
    "warning":  "#B08900",   # soft amber
    "risk":     "#4B5563",   # charcoal
}



# kpi
def kpi(title, value, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H3(value, className=f"text-{color}")
        ]),
        className="shadow-sm"
    )

def asset_kpi_row(df):
  return dbc.Row(
          [
            dbc.Col(kpi("Total Assets", len(df), "white")),
            dbc.Col(kpi("Average Price", df['price'].mean().round(decimals=2), "success")),
            dbc.Col(kpi("Volatity", df['volatility_30d'].mean().round(decimals=4), "success"))
          ],
          className="mb-4"
        )
  
  
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

def asset_kpi_section(data):
    if isinstance(data, list):
        data = data[-1]

    price: float = data.get("price", 0)
    drawdown: float = data.get("pct_drawdown", 0)
    trend: str = data.get("trend", "")
    volatility: float = data.get("volatility_30d", 0)
    dca_bias: float = data.get("dca_bias", 0)

    price_fmt      = f"${price:,.2f}"
    drawdown_fmt   = f"{drawdown:.2f}%"
    volatility_fmt = f"{volatility:.4f}"
    dca_bias_fmt   = f"{dca_bias:.4f}"

    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Price"), html.H4(price_fmt)]),
                         color=PALETTE["neutral"], inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("30D Drawdown"), html.H4(drawdown_fmt)]),
                         color=kpi_color(drawdown, "drawdown"), inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Trend"), html.H4(trend)]),
                         color=kpi_color(trend, "trend"), inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Volatility (30D)"), html.H4(volatility_fmt)]),
                         color=kpi_color(volatility, "volatility"), inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("DCA Bias"), html.H4(dca_bias_fmt)]),
                         color=kpi_color(dca_bias, "dca"), inverse=True)),
    ], className="mb-4 g-2 row-cols-2 row-cols-md-5")

def asset_kpi_section_empty():
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Price"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("30D Drawdown"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Trend"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Volatility (30D)"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True)),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("DCA Bias"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True)),
    ], className="mb-4 g-2 row-cols-2 row-cols-md-5")