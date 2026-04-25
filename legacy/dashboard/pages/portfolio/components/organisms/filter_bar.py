"""Organism — workspace filter bar and advanced filter panel."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..atoms.dropdown import tv_dropdown

OPTIONAL_COLUMNS = [
    {"label": "Cumul. Return", "value": "cumulative_value_return"},
    {"label": "Daily Return", "value": "daily_value_return"},
    {"label": "MA Signal", "value": "value_ma_crossover_signal"},
    {"label": "Price", "value": "price"},
    {"label": "Avg Cost", "value": "avg_price"},
    {"label": "Weight %", "value": "weight_pct"},
    {"label": "30D High", "value": "recent_profit_high_30d"},
    {"label": "% Drawdown", "value": "price_drawdown_pct_30d"},
    {"label": "Vol 30D", "value": "volatility_30d"},
    {"label": "VaR 95%", "value": "var_95_1d"},
    {"label": "DCA Bias", "value": "dca_bias"},
    {"label": "Date", "value": "data_date"},
]

DEFAULT_VISIBLE_COLS = [col["value"] for col in OPTIONAL_COLUMNS]


TIMEFRAMES = [
    {"label": "1D", "value": "1D"},
    {"label": "1W", "value": "1W"},
    {"label": "1M", "value": "1M"},
    {"label": "3M", "value": "3M"},
    {"label": "6M", "value": "6M"},
    {"label": "1Y", "value": "1Y"},
    {"label": "All", "value": "All"},
]


def workspace_filter_bar():
    return html.Div(
        [
            # Advanced filter toggle (primary action — filled)
            dbc.Button(
                [html.I(className="fa-solid fa-sliders me-1"), "Advanced Filter"],
                id="workspace-adv-filter-btn",
                className="tv-apply-btn",
                size="sm",
                n_clicks=0,
            ),
            html.Div(className="tv-vert-divider"),
            # Timeframe strip
            dcc.RadioItems(
                id="workspace-timeframe-selector",
                options=TIMEFRAMES,
                value="1Y",
                className="tv-timeframe-strip",
                inputStyle={"display": "none"},
            ),
            html.Div(className="tv-vert-divider"),
            # Tag filter dropdown
            tv_dropdown(
                id="workspace-tag-filter",
                multi=True,
                placeholder="Filter by tag…",
                style={"minWidth": "180px", "fontSize": "12px"},
            ),
            # Spacer pushes advanced filter to the right
            html.Div(style={"marginLeft": "auto"}),
            dbc.Button(
                [html.I(className="fa-solid fa-plus me-1"), "Create Tag"],
                id="btn-create-tag",
                className="tv-ghost-btn",
                size="sm",
                n_clicks=0,
            ),
            # Vertical divider
            html.Div(className="tv-vert-divider"),
            # Column visibility toggle
            dbc.Button(
                html.I(className="fa-solid fa-eye"),
                id="column-toggle-btn",
                className="tv-ghost-btn",
                size="sm",
                n_clicks=0,
                title="Show/hide columns",
            ),
            html.Div(className="tv-vert-divider"),
            # Rebalancing panel toggle
            dbc.Button(
                html.I(className="fa-solid fa-scale-balanced"),
                id="rebalance-panel-toggle-btn",
                className="tv-ghost-btn",
                size="sm",
                n_clicks=0,
                title="Toggle rebalancing panel",
            ),
            html.Div(className="tv-vert-divider"),
        ],
        className="workspace-filter-bar",
    )


def column_visibility_popover():
    """Floating popover anchored to column-toggle-btn."""
    return dbc.Popover(
        dbc.PopoverBody(
            dcc.Checklist(
                id="column-visibility-checklist",
                options=OPTIONAL_COLUMNS,
                value=DEFAULT_VISIBLE_COLS,
                labelStyle={
                    "display": "block",
                    "fontSize": "12px",
                    "marginBottom": "4px",
                },
            )
        ),
        id="column-visibility-popover",
        target="column-toggle-btn",
        trigger="legacy",
        placement="bottom-end",
        is_open=False,
    )


def workspace_advanced_filter():
    """Collapsible advanced filter panel rendered below the filter bar."""
    return dbc.Collapse(
        html.Div(
            [
                html.Span("From", className="tv-date-label"),
                dcc.DatePickerSingle(
                    id="workspace-start-date",
                    placeholder="Start date",
                    display_format="DD MMM YYYY",
                    className="tv-single-picker",
                ),
                html.Span("To", className="tv-date-label"),
                dcc.DatePickerSingle(
                    id="workspace-end-date",
                    placeholder="End date",
                    display_format="DD MMM YYYY",
                    className="tv-single-picker",
                ),
                dbc.Button(
                    "Apply",
                    id="workspace-apply-filter-btn",
                    className="tv-apply-btn",
                    size="sm",
                    n_clicks=0,
                ),
            ],
            className="tv-collapse-body",
        ),
        id="workspace-adv-filter-collapse",
        is_open=False,
    )
