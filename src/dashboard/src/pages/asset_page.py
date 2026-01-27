import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback, dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.tables.asset import asset_table
from src.dashboard.src.services.asset_service import AssetService
from src.dashboard.src.styles.style import TAB_CONTENT_STYLE

# ─────────────────────────────────────────────
# Data prep
# ─────────────────────────────────────────────
def prep_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["data_datetime"] = pd.to_datetime(df["data_date"])
    df["pct_drawdown"] = (df["price"] - df["recent_high_30d"]) / df["recent_high_30d"]
    df["price_vs_ma_50"] = np.where(
        df["ma_50"] != 0, (df["price"] - df["ma_50"]) / df["ma_50"], None
    )
    df["volatility_30d"] = df.groupby("asset_id")["price"].pct_change().rolling(30).std()
    df["dca_bias"] = -0.5 * df["pct_drawdown"] - 0.4 * df["price_vs_ma_50"] + 0.1 * df["volatility_30d"]
    return df

asset_df = prep_data(AssetService.get_asset_data("2026-01-20", "2026-01-27"))
ASSET_NAMES = asset_df["name"].unique().tolist()

# ─────────────────────────────────────────────
# KPI logic
# ─────────────────────────────────────────────
def compute_asset_kpis(asset_name: str) -> dict:
    x = asset_df[asset_df["name"] == asset_name].sort_values("data_datetime").iloc[-1]
    trend = "Bullish" if x["ma_30"] > x["ma_50"] else "Bearish"
    return {
        "price": round(x["price"], 2),
        "drawdown": round(x["pct_drawdown"] * 100, 2),
        "volatility": round(x["volatility_30d"], 4),
        "trend": trend,
        "dca_bias": round(x["dca_bias"], 3),
    }

def kpi_color(value, kind):
    if kind == "drawdown":
        return "success" if value < -5 else "warning" if value < -2 else "danger"
    if kind == "trend":
        return "success" if value == "Bullish" else "danger"
    if kind == "volatility":
        return "warning" if value > 0.02 else "success"
    if kind == "dca":
        return "success" if value > 0 else "danger"
    return "secondary"

def asset_kpi_section(asset_name: str):
    k = compute_asset_kpis(asset_name)
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

# ─────────────────────────────────────────────
# Figures
# ─────────────────────────────────────────────
def fig_profit_by_date(asset_name: str):
    x = asset_df[asset_df["name"] == asset_name].sort_values("data_datetime")
    fig = px.line(x, x="data_datetime", y="profit", title="Profit over time")
    fig.update_layout(template="plotly_white", height=350)
    fig.update_traces(connectgaps=False, line=dict(color="#1f77b4", width=2))
    return fig

def fig_ma_by_date(asset_name: str):
    x = asset_df[asset_df["name"] == asset_name].sort_values("data_datetime")
    fig = px.line(x, x="data_datetime", y=["ma_30", "ma_50"], title="Moving Averages")
    fig.for_each_trace(lambda t: t.update(name="30-day MA" if t.name=="ma_30" else "50-day MA"))
    fig.update_layout(template="plotly_white", height=350, legend_title_text="MA")
    fig.update_traces(connectgaps=False, line=dict(width=2))
    return fig

def fig_drawdown(asset_name: str):
    x = asset_df[asset_df["name"] == asset_name].sort_values("data_datetime")
    fig = px.line(x, x="data_datetime", y="pct_drawdown", title="Drawdown vs Recent High")
    fig.update_layout(template="plotly_white", height=350)
    fig.update_traces(connectgaps=False, line=dict(color="#ff7f0e", width=2))
    return fig

def fig_dca_bias(asset_name: str):
    x = asset_df[asset_df["name"] == asset_name].sort_values("data_datetime")
    fig = px.line(x, x="data_datetime", y="dca_bias", title="DCA Bias over Time")
    fig.update_layout(template="plotly_white", height=350)
    fig.update_traces(connectgaps=False, line=dict(color="#2ca02c", width=2))
    return fig

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
def assets_tab(df):
    return card("Assets", asset_table(df))

def monitoring_tab():
    return html.Div([
        dbc.Row([
            dbc.Col(dbc.Select(id="assetpage_asset_select",
                               options=[{"label": a, "value": a} for a in ASSET_NAMES],
                               value=ASSET_NAMES[0]), md=4)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="profit_graph"), md=6),
            dbc.Col(dcc.Graph(id="ma_graph"), md=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="drawdown_graph"), md=6),
            dbc.Col(dcc.Graph(id="dca_graph"), md=6)
        ])
    ])

# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def asset_layout(df):
    return html.Div([
        html.Div(id="asset_kpi_container"),
        dbc.Tabs([
            dbc.Tab(assets_tab(df), label="Assets", style=TAB_CONTENT_STYLE),
            dbc.Tab(monitoring_tab(), label="Monitoring", style=TAB_CONTENT_STYLE),
        ])
    ])

# ─────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────
@callback(
    Output("asset_kpi_container", "children"),
    Output("profit_graph", "figure"),
    Output("ma_graph", "figure"),
    Output("drawdown_graph", "figure"),
    Output("dca_graph", "figure"),
    Input("assetpage_asset_select", "value")
)
def update_asset_page(asset_name):
    if asset_name is None:
        raise dash.exceptions.PreventUpdate

    return (
        asset_kpi_section(asset_name),
        fig_profit_by_date(asset_name),
        fig_ma_by_date(asset_name),
        fig_drawdown(asset_name),
        fig_dca_bias(asset_name)
    )