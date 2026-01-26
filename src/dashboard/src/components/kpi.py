import dash_bootstrap_components as dbc
from dash import html

# kpi
def kpi(title, value, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H3(value, className=f"text-{color}")
        ]),
        className="shadow-sm"
    )

def kpi_row(df):
  return dbc.Row(
          [
            dbc.Col(kpi("Portfolio Value", "€100", "white")),
            dbc.Col(kpi("Unrealized P&L", "+€50", "success")),
            dbc.Col(kpi("Realized P&L", "+€60", "success"))
          ],
          className="mb-4"
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