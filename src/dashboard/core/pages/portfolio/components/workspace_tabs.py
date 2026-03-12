import dash_bootstrap_components as dbc
from dash import dcc, html

from .charts import (
    WinnersPlotlyBarChart,
    LosersPlotlyBarChart,
    PortfolioPerformancePlotlyLineChart,
    PortfolioPNLPlotlyLineChart,
    PositionWeightPlotlyBarChart,
)
from ...asset.components.charts import (
    PriceStructurePlotlyLineChart,
    AssetValuePlotlyLineChart,
    RiskContextPlotlyLineChart,
    DCABiasPlotlyLineChart,
    AssetCategoryPlotlyPieChart,
    AssetTagsPlotlyPieChart,
)

_GRAPH_CONFIG = {"displayModeBar": False}
_CENTERED_LOADER_STYLE = {
    "position": "absolute", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"
}


def _chart_section(title, chart):
    return html.Div([
        html.Div([title, html.Span("›", className="tv-chevron")], className="tv-section-header"),
        chart,
    ])


# ─────────────────────────────────────────────
# Portfolio tab content
# ─────────────────────────────────────────────

def portfolio_tab_content(view_model=None, theme="light"):
    if view_model is None:
        return html.Div(
            html.P("Loading portfolio charts…", className="text-muted text-center py-5"),
            id="tab-portfolio-content",
        )

    rows = view_model.get("asset_table", {}).get("rows", [])
    value_series = view_model.get("portfolio_value_series", {})
    pnl_series = view_model.get("portfolio_pnl_series", {})
    position_weight_series = view_model.get("position_weight_series", [])

    return html.Div([
        html.Div([
            _chart_section("Portfolio Value", dcc.Graph(
                id="value_chart",
                figure=PortfolioPerformancePlotlyLineChart().render(value_series, theme=theme),
                config=_GRAPH_CONFIG,
            )),
            _chart_section("Profit & Loss", dcc.Graph(
                id="pnl_char",
                figure=PortfolioPNLPlotlyLineChart().render(pnl_series, theme=theme),
                config=_GRAPH_CONFIG,
            )),
            
        ], className="workspace-chart-grid"),
        
        html.Hr(className="tv-divider"),
        html.Div([
            _chart_section("Asset Category", dcc.Graph(
                id="asset_category_chart",
                figure=AssetCategoryPlotlyPieChart().render(value_series, theme=theme),
                config=_GRAPH_CONFIG,
            )),
            _chart_section("Asset Tags", dcc.Graph(
                id="asset_tags_chart",
                figure=AssetTagsPlotlyPieChart().render(value_series, theme=theme),
                config=_GRAPH_CONFIG,
            )),
        ], className="workspace-chart-grid"),
        
        html.Hr(className="tv-divider"),
        html.Div([
            _chart_section("Top Winners", dcc.Graph(
                id="winners_chart",
                figure=WinnersPlotlyBarChart().render(rows, theme=theme),
                config=_GRAPH_CONFIG,
            )),
            _chart_section("Top Losers", dcc.Graph(
                id="losers_chart",
                figure=LosersPlotlyBarChart().render(rows, theme=theme),
                config=_GRAPH_CONFIG,
            )),
        ], className="workspace-chart-grid"),

        html.Hr(className="tv-divider"),
        html.Div([
            _chart_section("Position Weight", dcc.Graph(
                id="position_weight_chart",
                figure=PositionWeightPlotlyBarChart().render(position_weight_series, theme=theme),
                config=_GRAPH_CONFIG,
            )),
        ], className="workspace-chart-grid"),
    ], id="tab-portfolio-content")


# ─────────────────────────────────────────────
# Valuation tab content
# ─────────────────────────────────────────────

def valuation_tab_content(asset_history=None, theme="light"):
    if asset_history is None:
        return html.Div(
            html.P(
                "Select an asset from the table to view valuation charts.",
                className="text-muted text-center py-5",
            ),
            id="tab-valuation-content",
        )

    return html.Div([
        html.Div([
            _chart_section("Profit Over Time", 
                dcc.Graph(
                    id="workspace-price-graph",
                    figure=PriceStructurePlotlyLineChart().render(asset_history, theme=theme),
                    config=_GRAPH_CONFIG,
                ),
            ),
                
            _chart_section("Asset Value Over Time", 
                dcc.Graph(
                    id="workspace-value-graph",
                    figure=AssetValuePlotlyLineChart().render(asset_history, theme=theme),
                    config=_GRAPH_CONFIG,
                )
        ),
            
        ], className="workspace-chart-grid"),
        
        
        html.Div([
            
            _chart_section("Risk Context - Drawdown", 
                dcc.Graph(
                    id="workspace-risk-graph",
                    figure=RiskContextPlotlyLineChart().render(asset_history, theme=theme),
                    config=_GRAPH_CONFIG,
                )
            ),
            _chart_section("Opportunity - DCA Bias", 
                dcc.Graph(
                    id="workspace-dca-graph",
                    figure=DCABiasPlotlyLineChart().render(asset_history, theme=theme),
                    config=_GRAPH_CONFIG,
                )
            )
            
        ], className="workspace-chart-grid"),
    ], id="tab-valuation-content")


# ─────────────────────────────────────────────
# Risk tab content (placeholder)
# ─────────────────────────────────────────────

def risk_tab_content():
    return html.Div([
        html.Div([
            html.I(className="fa-solid fa-shield-halved fa-2x mb-3", style={"color": "var(--text-muted)"}),
            html.P("Risk analysis coming soon.", className="text-muted mb-1"),
            html.P("Select an asset to explore risk metrics.", className="text-muted", style={"fontSize": "12px"}),
        ], className="text-center py-5"),
    ], id="tab-risk-content")


# ─────────────────────────────────────────────
# Opportunities tab content (placeholder)
# ─────────────────────────────────────────────

def opportunities_tab_content():
    return html.Div([
        html.Div([
            html.I(className="fa-solid fa-chart-line fa-2x mb-3", style={"color": "var(--text-muted)"}),
            html.P("Opportunities analysis coming soon.", className="text-muted mb-1"),
            html.P("Select an asset and apply filters to explore.", className="text-muted", style={"fontSize": "12px"}),
        ], className="text-center py-5"),
    ], id="tab-opportunities-content")


# ─────────────────────────────────────────────
# Full tab widget
# ─────────────────────────────────────────────

def workspace_tabs(view_model=None, theme="light"):
    """Renders the 4-tab workspace panel. Call on page load with portfolio view_model."""
    return dbc.Tabs(
        id="workspace-tabs",
        active_tab="tab-portfolio",
        className="workspace-tab-bar mb-0",
        children=[
            dbc.Tab(
                label="Portfolio",
                tab_id="tab-portfolio",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=dcc.Loading(
                    id="loading-portfolio-tab",
                    type="circle",
                    style=_CENTERED_LOADER_STYLE,
                    children=portfolio_tab_content(view_model, theme),
                ),
            ),
            dbc.Tab(
                label="Valuation",
                tab_id="tab-valuation",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=dcc.Loading(
                    id="loading-valuation-tab",
                    type="circle",
                    style=_CENTERED_LOADER_STYLE,
                    children=valuation_tab_content(theme=theme),
                ),
            ),
            dbc.Tab(
                label="Risk",
                tab_id="tab-risk",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=risk_tab_content(),
            ),
            dbc.Tab(
                label="Opportunities",
                tab_id="tab-opportunities",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=opportunities_tab_content(),
            ),
        ],
    )
