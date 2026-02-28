from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import date, datetime, UTC


def asset_page_filter(data):
    
    TIMEFRAMES = {
        0: ("1D", 0),
        1: ("1W", 7),
        2: ("1M", 30),
        3: ("3M", 90),
        4: ("6M", 180),
        5: ("1Y", 365),
        6: ("ALL", None),
    }
    return dbc.Row(
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                                data.get("rows", []),
                                # options=[{"label": a, "value": a} for a in ASSET_NAMES],
                                multi=True,
                                id="assetpage_asset_select"), md=4),
            dbc.Col([
                dcc.DatePickerRange(
                    id="asset_page_date_picker_filter",
                    className="asset-date-picker",
                    min_date_allowed=date(2020, 1, 1),
                    max_date_allowed=date(2049, 12, 31),
                    initial_visible_month=datetime.now(),
                    start_date_placeholder_text="Start",
                    end_date_placeholder_text="End",
                )
            ], md=2),
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
            ], md=2),
            dbc.Col([
                dbc.Button("Submit", id="asset_page_filter_btn")
            ], md=2)
        ], className="mb-3")
    )