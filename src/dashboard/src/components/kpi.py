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
            dbc.Col(kpi("Portfolio Value", "€12,430", "white")),
            dbc.Col(kpi("Unrealized P&L", "+€1,240", "success")),
            dbc.Col(kpi("Realized P&L", "+€860", "success"))
          ],
          className="mb-4"
        )

def asset_kpi_row(df):
  return dbc.Row(
          [
            dbc.Col(kpi("Drawdown", "€12,430", "white")),
            dbc.Col(kpi("Average Price", "+€1,240", "success")),
            dbc.Col(kpi("Volatity", "+€860", "success"))
          ],
          className="mb-4"
        )