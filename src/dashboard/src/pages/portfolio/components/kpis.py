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


def kpi_row(data={}):
  currency = data.get("currency", "#")
  
  currency_sign = '€' if currency == 'EUR' else '$'
  value = data.get("value", 0)
  value = 100
  realized_pnl = data.get("realized_pnl", 0)
  total_invested = data.get("total_cost", 0)
  total_invested = 200
  unrealized_pnl = data.get("unrealized_pnl", 0)
  
  value_str = f'{currency_sign}{value}'
  total_invested_str = f'{currency_sign}{total_invested}'
  realized_pnl_str = f'{currency_sign}{realized_pnl}'
  unrealized_pnl_str = f'{currency_sign}{unrealized_pnl}'
  beta = 1
  
  return dbc.Row(
          [
            dbc.Col(kpi("Portfolio Value", value=value_str)),
            dbc.Col(kpi("Total Invested", value=total_invested_str)),
            dbc.Col(kpi("Unrealized P&L", value=realized_pnl_str, color="success")),
            dbc.Col(kpi("Realized P&L", value=unrealized_pnl_str, color="success")),
            dbc.Col(kpi("Beta", value=beta, color="success"))
          ],
          className="mb-4"
        )