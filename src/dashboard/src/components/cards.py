import dash_bootstrap_components as dbc
from dash import dcc

def card(header, figure):
  return dbc.Card([
    dbc.CardHeader(header),
    dbc.CardBody(
      figure, className='p-0'
  )], className="shadow-sm h-100 w-100")