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
from src.dashboard.src.components.cards import card
from src.dashboard.src.pages.asset.tables import asset_table
from src.dashboard.src.services.asset_service import AssetService
from src.dashboard.src.styles.style import TAB_CONTENT_STYLE
# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
from src.dashboard.src.pages.asset.charts import ProfitOverTimePlotlyLineChart, MovingAveragePriceOverTimePlotlyLineChart, RecentHeighDrawdownOverTimePlotlyLineChart, DollarCostAVGBiasOverTimePlotlyLineChart
# ─────────────────────────────────────────────
# Data prep
# ─────────────────────────────────────────────
# TODO: MOVE LOGIC TO SERVICE LAYER
def prep_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["pct_drawdown"] = (df["price"] - df["recent_high_30d"]) / df["recent_high_30d"]
    df["price_vs_ma_50"] = np.where(
        df["ma_50"] != 0, (df["price"] - df["ma_50"]) / df["ma_50"], None
    )
    df["volatility_30d"] = df.groupby("asset_id")["price"].pct_change().rolling(30).std()
    df["dca_bias"] = -0.5 * df["pct_drawdown"] - 0.4 * df["price_vs_ma_50"] + 0.1 * df["volatility_30d"]
    df["trend"] = df[["ma_30", "ma_50"]].apply(lambda x: "Bullish" if x["ma_30"] > x["ma_50"] else "Bearish", axis=1)
    return df

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
    df = pd.DataFrame(data)
    k = compute_asset_kpis(df)
    return dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Price"), html.H4(k["price"])])), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("30D Drawdown"), html.H4(f"{k['drawdown']}%")]),
                         color=kpi_color(k["drawdown"], "drawdown"), inverse=True), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Trend"), html.H4(k["trend"])]),
                         color=kpi_color(k["trend"], "trend"), inverse=True), md=2),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("Volatility (30D)"), html.H4(k["volatility"])]),
                         color=kpi_color(k["volatility"], "volatility"), inverse=True), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.Small("DCA Bias"), html.H4(k["dca_bias"])]),
                         color=kpi_color(k["dca_bias"], "dca"), inverse=True), md=3),
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
    df = pd.DataFrame(data)
    ASSET_NAMES = sorted(df["asset_description"].unique())
    return dbc.Row(
        dbc.Row([
            dbc.Col(dbc.Select(id="assetpage_asset_select",
                                options=[{"label": a, "value": a} for a in ASSET_NAMES],
                                value=ASSET_NAMES[0]), md=4),
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
            ], md=4),
            dbc.Col([
                dbc.Button("Submit", id="asset_page_filter_btn")
            ], md=4)
        ], className="mb-3")
    )


def chart_tab(data):
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="profit_graph", figure=ProfitOverTimePlotlyLineChart().render(data)), md=6),
            dbc.Col(dcc.Graph(id="ma_graph", figure=MovingAveragePriceOverTimePlotlyLineChart().render(data)), md=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="drawdown_graph", figure=RecentHeighDrawdownOverTimePlotlyLineChart().render(data)), md=6),
            dbc.Col(dcc.Graph(id="dca_graph", figure=DollarCostAVGBiasOverTimePlotlyLineChart().render(data)), md=6)
        ])
    ], id="asset_page_chart_tab")

def chart_tab_empty():
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="profit_graph"), md=6),
            dbc.Col(dcc.Graph(id="ma_graph"), md=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="drawdown_graph"), md=6),
            dbc.Col(dcc.Graph(id="dca_graph"), md=6)
        ])
    ], id="asset_page_chart_tab")

def page_content():
    return dbc.Tabs([
                dbc.Tab(id="asset_tab", children=[dag.AgGrid()], label="Assets", style=TAB_CONTENT_STYLE),
                dbc.Tab(id="asset_chart_tab", children=chart_tab_empty(), label="Charts", style=TAB_CONTENT_STYLE),
            ])
# ─────────────────────────────────────────────
# Page layout
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
    asset_key = asset_name.strip().lower()

    asset_data = pd.DataFrame(data)

    # normalize description column
    asset_data["asset_description_norm"] = (
        asset_data["asset_description"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    asset_data_df = asset_data[
        asset_data["asset_description_norm"] == asset_key
    ].to_dict("records")

    asset_snapshot = AssetService.get_asset_snapshot(start_date, end_date)
    asset_snapshot_df = prep_data(asset_snapshot)

    if asset_snapshot_df.empty:
        raise PreventUpdate

    asset_snapshot_df["asset_description_norm"] = (
        asset_snapshot_df["asset_description"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    asset_snapshot_data = asset_snapshot_df[
        asset_snapshot_df["asset_description_norm"] == asset_key
    ].to_dict("records")

    if len(asset_snapshot_data) == 0 or len(asset_data_df) == 0:
        raise PreventUpdate
    return (
        asset_kpi_section(asset_data_df),
        chart_tab(asset_snapshot_data)
    )

@callback(
    Output("asset_page_asset_store", "data"),
    Output("asset_page_filter_container", "children"),
    Output("asset_tab", "children"),
    Input("asset_page_location", "pathname"),
)
def load_asset_page(pathname):
    if pathname != "/assets":
        raise PreventUpdate
    df = AssetService.get_asset_data()
    if df.empty:
        raise PreventUpdate
    data = df.to_dict("records")
    return (
        data,
        asset_page_filter(data),
        asset_table(df),
    )