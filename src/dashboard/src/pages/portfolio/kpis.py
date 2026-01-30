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


def kpi_row():
  return dbc.Row(
          [
            dbc.Col(kpi("Portfolio Value", "€100")),
            dbc.Col(kpi("Unrealized P&L", "+€50", "success")),
            dbc.Col(kpi("Realized P&L", "+€60", "success"))
          ],
          className="mb-4"
        )