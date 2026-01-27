import dash_bootstrap_components as dbc
from dash import dcc, html

# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from src.dashboard.src.components.kpi import kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.portfolio import (
    portfolio_performance_chart,
)
from src.dashboard.src.components.tables.portfolio import (
    portfolio_timeseries_table,
)


# ─────────────────────────────────────────────
# Section builders
# ─────────────────────────────────────────────
def performance_section(df):
    return card(
        "Performance",
        dcc.Graph(
            figure=portfolio_performance_chart(df),
            config={"displayModeBar": False},
        ),
    )


def history_section(df):
    return card(
        "History",
        portfolio_timeseries_table(df),
    )


# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def portfolio_layout(df):
    return html.Div([

        # KPIs
        kpi_row(df),

        # Main content
        dbc.Row([
            dbc.Col(
                performance_section(df),
                md=8,
                className="mt-4",
            ),
            dbc.Col(
                history_section(df),
                md=4,
                className="mt-4",
            ),
        ])
    ])