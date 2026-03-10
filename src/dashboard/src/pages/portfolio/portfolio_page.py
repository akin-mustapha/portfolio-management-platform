import dash_bootstrap_components as dbc
from dash import dcc, html

from .callbacks import load_portfolio_page
# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from .components.kpis import kpi_row
from .components.charts import performance_chart, value_chart, pnl_chart
from .components.tables import asset_table


# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────
def _section_header(title):
    return html.Div([
        html.Hr(className="tv-divider"),
        html.Div([
            html.Span(title),
            html.Span("›", className="tv-chevron"),
        ], className="tv-section-header"),
    ])


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
        _section_header("Holdings"),
        dbc.Row([
            dbc.Col(
                children=asset_section(),
            ),
        ]),
        _section_header("Performance"),
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
        html.Hr(className="tv-divider"),
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.Span("Winners & Losers"),
                    html.Span("›", className="tv-chevron"),
                ], className="tv-section-header mb-0"),
                width="auto",
            ),
            dbc.Col(
                dbc.Select(
                    id="winners_losers_count",
                    options=[{"label": f"Top {n}", "value": n} for n in [5, 10, 15, 20]],
                    value=10,
                    size="sm",
                    style={"width": "90px"},
                ),
                width="auto",
                className="ms-2",
            ),
        ], align="center", className="mb-2"),
        html.Div(
            id="portfolio_page_charts_container",
            children=performance_chart(),
        ),
    ])
