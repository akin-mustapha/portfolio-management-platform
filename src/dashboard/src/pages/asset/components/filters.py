from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
from dash import html

TIMEFRAMES = {
    0: ("1D", 0),
    1: ("1W", 7),
    2: ("1M", 30),
    3: ("3M", 90),
    4: ("6M", 180),
    5: ("1Y", 365),
    6: ("ALL", None),
}


def asset_page_filter(data):
    return dbc.Card([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    data.get("rows", []),
                    # options=[{"label": a, "value": a} for a in ASSET_NAMES],
                    value=data.get("rows", [None])[0],
                    multi=True,
                    placeholder="Select an asset...",
                    id="assetpage_asset_select"),
                md=4),
            dbc.Col([
                html.Div([
                    html.Label("Timeframe"),
                    dcc.Slider(
                        id="date-slider",
                        className="timeframe-slider",
                        min=0,
                        max=len(TIMEFRAMES) - 1,
                        value=0,  # default = 1Y
                        step=1,
                        marks={k: v[0] for k, v in TIMEFRAMES.items()},
                    )
                ]),
            ], md=5),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Advanced Filter",
                    id="collapse-button",
                    className="mb-2",
                    size="sm",
                    color="primary",
                    n_clicks=0,
                ),
            ], md=12),
        ]),
        dbc.Collapse(
            dbc.Row([
                dbc.Col(
                    dcc.DatePickerRange(
                        id="asset_page_date_picker_filter",
                        className="asset-date-picker",
                        min_date_allowed=date(2020, 1, 1),
                        max_date_allowed=date(2049, 12, 31),
                        initial_visible_month=datetime.now(),
                        start_date=date.today() - timedelta(days=1),
                        end_date=date.today(),
                        start_date_placeholder_text="Start date",
                        end_date_placeholder_text="End date",
                    ), md=4
                ),
                dbc.Col(
                    dbc.Button("Submit", id="asset_page_filter_btn", size="sm"),
                    md=1
                ),
            ], className="mt-2"),
            id="collapse",
            is_open=False,
        ),
    ], body=True, className="mb-3")
    
