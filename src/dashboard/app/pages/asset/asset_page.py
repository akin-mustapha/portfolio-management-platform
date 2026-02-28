import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback, State
from datetime import date
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from datetime import datetime, UTC
import dash_ag_grid as dag

# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from src.dashboard.app.components.cards import card
from src.dashboard.app.pages.asset.tables import asset_table
from src.dashboard.app.controllers.asset_controller import AssetController
# from src.dashboard.services.local_asset_service import LocalAssetController
from src.dashboard.app.styles.style import TAB_CONTENT_STYLE
# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
from src.dashboard.app.pages.asset.charts import PriceStructurePlotlyLineChart, AssetValuePlotlyLineChart, RiskContextPlotlyLineChart, DCABiasPlotlyLineChart
# ─────────────────────────────────────────────
# Data prep
# ─────────────────────────────────────────────
# KPI logic
# ─────────────────────────────────────────────
def compute_asset_kpis(df) -> dict:
    x = df.sort_values("data_date").iloc[-1]
    return {
        "price": round(x["price"], 2),
        "drawdown": round(x["pct_drawdown"] * 100, 2),
        "volatility": round(x["volatility_30d"], 4),
        "trend": x["trend"],
        "dca_bias": round(x["dca_bias"], 3),
    }

PALETTE = {
    "positive": "#2F6F6A",   # muted teal
    "neutral":  "#6B7280",   # slate gray
    "warning":  "#B08900",   # soft amber
    "risk":     "#4B5563",   # charcoal
}

def kpi_color(value, kind):
    if kind == "drawdown":
        if value <= -8:
            return PALETTE["risk"]
        elif value <= -4:
            return PALETTE["warning"]
        else:
            return PALETTE["neutral"]

    if kind == "trend":
        return PALETTE["positive"] if value == "Bullish" else PALETTE["neutral"]

    if kind == "volatility":
        if value >= 0.04:
            return PALETTE["risk"]
        elif value >= 0.02:
            return PALETTE["warning"]
        else:
            return PALETTE["neutral"]

    if kind == "dca":
        return PALETTE["positive"] if value > 0 else PALETTE["neutral"]
    
    return PALETTE["neutral"]

def asset_kpi_section(data):
    if isinstance(data, list):
        data = data[-1]
    
    price: float = data.get("price", 0)
    drawdown: float = data.get("pct_drawdown", 0)
    trend: str = data.get("trend", "")
    volatility: float = data.get("volatility_30d", 0)
    dca_bias: float = data.get("dca_bias", 0)
    
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Price"), html.H4(price)])), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("30D Drawdown"), html.H4(f"{drawdown}%")]),
                         color=kpi_color(drawdown, "drawdown"), inverse=True), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Trend"), html.H4(trend)]),
                         color=kpi_color(trend, "trend"), inverse=True), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Volatility (30D)"), html.H4(volatility)]),
                         color=kpi_color(volatility, "volatility"), inverse=True), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("DCA Bias"), html.H4(dca_bias)]),
                         color=kpi_color(dca_bias, "dca"), inverse=True), md=3),
    ], className="mb-4")

def asset_kpi_section_empty():
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Price"), html.H4("—")])), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("30D Drawdown"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Trend"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Volatility (30D)"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("DCA Bias"), html.H4("—")]),
                         color=PALETTE["neutral"], inverse=True), md=3),
    ], className="mb-4")
# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
def assets_tab(df):
    return card("Assets", asset_table(df), className='mb-4')

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
# Duplicate logic. Needed
# Might want to move graphs
def chart_tab(data):
    return html.Div([

        dbc.Row([
            dbc.Col(dcc.Graph(id="price_graph", figure=PriceStructurePlotlyLineChart
().render(data)), md=6),
            dbc.Col(dcc.Graph(id="value_graph", figure=AssetValuePlotlyLineChart().render(data)), md=6)
        ], className="mb-3"),


        dbc.Row([
            dbc.Col(dcc.Graph(id="risk_graph", figure=RiskContextPlotlyLineChart().render(data)), md=6),
            dbc.Col(dcc.Graph(id="dca_graph", figure=DCABiasPlotlyLineChart().render(data)), md=6)
        ], className="mb-3"),

        # dbc.Row([
        #     dbc.Col(dcc.Graph(id="drawdown_graph", figure=RecentHeighDrawdownOverTimePlotlyLineChart().render(data)), md=6),
        # ])
    ], id="asset_page_chart_tab")

def chart_tab_empty():
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="price_graph"), md=6),
            dbc.Col(dcc.Graph(id="value_graph"), md=6)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="risk_graph"), md=6),
            dbc.Col(dcc.Graph(id="dca_graph"), md=6)
        ], className="mb-3"),

        # dbc.Row([
        #     dbc.Col(dcc.Graph(id="drawdown_graph"), md=6),
        #     dbc.Col(dcc.Graph(id="dca_graph"), md=6)
        # ])
    ], id="asset_page_chart_tab")

def page_content():
    return dbc.Tabs([
        # Depreciated: Moved to portfolio page
        # dbc.Tab(id="asset_tab", children=[dag.AgGrid()], label="Assets", style=TAB_CONTENT_STYLE),
        dbc.Tab(id="asset_chart_tab", children=chart_tab_empty(), label="Charts", style=TAB_CONTENT_STYLE),
    ])
# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def asset_layout():
    return html.Div([
        dcc.Location(id="asset_page_location"),
        dcc.Store(id="asset_page_asset_store"),

        dbc.Row([
            dbc.Stack([
                html.Div(id="asset_kpi_container", children=[asset_kpi_section_empty()]),
                html.Div(id="asset_page_filter_container")
            ], gap=4)
        ]),

        dbc.Row(id="asset_page_content_container", children=[page_content()]),
    ], id="asset_page")
# ─────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────
@callback(
    Output("asset_kpi_container", "children"),
    Output("asset_page_chart_tab", "children"),
    Input("asset_page_filter_btn", "n_clicks"),
    State("asset_page_asset_store", "data"),
    State("assetpage_asset_select", "value"),
    State("asset_page_date_picker_filter", "start_date"),
    State("asset_page_date_picker_filter", "end_date"),
    prevent_initial_call=True
)
def update_asset_page(n_clicks, data, asset_name, start_date, end_date):
    if not all([data, asset_name, start_date, end_date]):
        raise PreventUpdate

    # normalize the selected value once
    if isinstance(asset_name, str):
        asset_name = [asset_name]
    asset_key = [name.strip().upper() for name in asset_name]
    
    view_model = data.get("view_model")
    
    asset_data = pd.DataFrame(view_model.get("asset_data"))
    
    mask = asset_data["ticker"].isin(asset_key)
    df_asset_data = asset_data[mask]

    df_asset_data = df_asset_data.to_dict("records")

    # TODO: UNCOMMENT TO CONNECT TO DB
    df_asset_data_history = AssetController().get_asset_snapshot(asset_key[0], start_date, end_date)

    # if df_asset_data_history.empty:
    #     raise PreventUpdate

    # if len(df_asset_data) == 0 or len(df_asset_data) == 0:
    #     raise PreventUpdate
    
    return (
        asset_kpi_section(df_asset_data),
        chart_tab(df_asset_data_history)
    )

@callback(
    Output("asset_page_asset_store", "data"),
    Output("asset_page_filter_container", "children"),
    # Depreciated: Moved to portfolio page
    # Output("asset_tab", "children"),
    Input("asset_page_location", "pathname"),
    State("asset_page_asset_store", "data"),
)
def load_asset_page(pathname, cached_data):
    if pathname != "/assets":
        raise PreventUpdate
    
    cached_data = cached_data or {}
    view_model =  cached_data.get("view_model", None)
    if view_model is None:
        view_model = AssetController().get_data()
        cached_data.update({"view_model": view_model})

    if view_model is None:
        raise PreventUpdate
    
    data = view_model.get('asset_filter')
    
    return (
        cached_data,
        asset_page_filter(data),
        # Depreciated: Moved to portfolio page
        # asset_table(df),
    )