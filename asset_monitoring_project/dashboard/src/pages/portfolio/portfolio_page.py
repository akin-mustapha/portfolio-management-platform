import dash_bootstrap_components as dbc
from dash import dcc, html

from .callbacks import load_portfolio_page
# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from dashboard.src.pages.portfolio.components.kpis import kpi_row

from .components.charts import performance_chart, value_chart, pnl_chart
from .components.tables import asset_table

# ─────────────────────────────────────────────
# Section builders
# ─────────────────────────────────────────────
def asset_section():
    return html.Div(
        id="portfolio_page_asset_table_container",
        children=[asset_table(None)],
    )
    
# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def portfolio_layout():
    return html.Div([
        dcc.Location(id="portfolio_page_location"),
        dcc.Store(id="portfolio_page_asset_store"),
        # KPIs
        dbc.Row([
            dbc.Col(
                id="portfolio_kpi_container",
                children=kpi_row(),
            )
        ]),
        dbc.Row([
            dbc.Col(
                children=asset_section(),
            ),
        ]),
        # Main content
        dbc.Row([
            dbc.Col(
                id="portfolio_page_value_chart_container",
                children=value_chart(),
                width="auto",
                md=6,
                ),
            dbc.Col(
                id="portfolio_page_pnl_chart_container",
                children=pnl_chart(),
                width="auto",
                md=6,
            )

        ]),
        html.Div(
            id="portfolio_page_charts_container",
            children=performance_chart(),
            ),
    ])
