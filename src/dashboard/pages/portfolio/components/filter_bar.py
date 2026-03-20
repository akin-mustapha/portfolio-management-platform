import dash_bootstrap_components as dbc
from dash import dcc, html


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
    return html.Div([
        
        # Timeframe strip
        dcc.RadioItems(
            id="workspace-timeframe-selector",
            options=TIMEFRAMES,
            value="1Y",
            className="tv-timeframe-strip",
            inputStyle={"display": "none"},
            labelStyle={
                "cursor": "pointer",
                "padding": "4px 10px",
                "fontSize": "12px",
                "fontWeight": "500",
                "borderRadius": "4px",
                "userSelect": "none",
            },
        ),
        html.Div(className="tv-vert-divider"),
        
        # Spacer pushes advanced filter to the right
        html.Div(style={"marginLeft": "auto"}),
        
        # Tag buttons
        dbc.Button(
            [html.I(className="fa-solid fa-tag me-1"), "Add Tag"],
            id="btn-add-tag",
            className="tv-adv-btn",
            size="sm",
            n_clicks=0,
        ),
        
        html.Div(className="tv-vert-divider"),
       
        dbc.Button(
            [html.I(className="fa-solid fa-plus me-1"), "Create Tag"],
            id="btn-create-tag",
            className="tv-adv-btn",
            size="sm",
            n_clicks=0,
        ),
        
        
        # Vertical divider
        html.Div(className="tv-vert-divider"),
        
         # Advanced filter toggle
        dbc.Button(
            [html.I(className="fa-solid fa-sliders me-1"), "Advanced Filter"],
            id="workspace-adv-filter-btn",
            className="tv-adv-btn",
            size="sm",
            n_clicks=0,
        ),

    ], className="workspace-filter-bar")


def workspace_advanced_filter():
    """Collapsible advanced filter panel rendered below the filter bar."""
    return dbc.Collapse(
        html.Div([
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
            dbc.Button("Apply", id="workspace-apply-filter-btn", className="tv-apply-btn", size="sm", n_clicks=0),
        ], className="tv-collapse-body"),
        id="workspace-adv-filter-collapse",
        is_open=False,
    )
