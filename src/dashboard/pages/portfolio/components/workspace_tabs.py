import dash_bootstrap_components as dbc
from dash import dcc, html

from .charts import (
    WinnersPlotlyBarChart,
    LosersPlotlyBarChart,
    PortfolioPerformancePlotlyLineChart,
    PortfolioPNLPlotlyLineChart,
    PositionWeightPlotlyDonutChart,
    PortfolioPerformanceScatterPlot,
    WinnersPnLPlotlyLineChart,
    LosersPnLPlotlyLineChart,
    PortfolioDrawdownPlotlyLineChart,
    PositionProfitabilityPlotlyDonutChart,
    VaRBarChart,
    DailyMoversBarChart,
)
from .asset_charts import (
    PriceStructurePlotlyLineChart,
    AssetValuePlotlyLineChart,
    RiskContextPlotlyLineChart,
    DCABiasPlotlyLineChart,
    ProfitRangePlotlyLineChart,
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


def _loading_placeholder(tab_id, message="Loading…"):
    return html.Div(
        html.P(message, className="text-muted text-center py-5"),
        id=tab_id,
    )


# ─────────────────────────────────────────────
# Portfolio tab content
# ─────────────────────────────────────────────

def portfolio_tab_content(view_model=None, theme="light"):
    if view_model is None:
        return _loading_placeholder("tab-portfolio-content", "Loading portfolio charts…")

    value_series = view_model.get("portfolio_value_series", {})
    pnl_series = view_model.get("portfolio_pnl_series", {})
    position_weight_series = view_model.get("position_weight_series", [])
    winners = view_model.get("winners", [])
    losers = view_model.get("losers", [])
    daily_movers = view_model.get("daily_movers", [])

    return html.Div([
        # ─────────────────────────────────────────────
        # Row: Performance (Value, PNL)
        # ─────────────────────────────────────────────
        dbc.Row([

            dbc.Col(
                _chart_section(
                    "Portfolio Value",
                    dcc.Graph(
                        id="value_chart",
                        figure=PortfolioPerformancePlotlyLineChart().render(value_series, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),

            dbc.Col(
                _chart_section(
                    "Portfolio P&L",
                    dcc.Graph(
                        id="pnl_chart",
                        figure=PortfolioPNLPlotlyLineChart().render(pnl_series, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),

        ], className="mb-6 workspace-chart-grid"),

        # ─────────────────────────────────────────────
        # Row: Winners | Losers + Position Weight
        # ─────────────────────────────────────────────
        html.Hr(className="tv-divider"),
        dbc.Row([

            dbc.Col(
                _chart_section(
                    "Top Losers",
                    dcc.Graph(
                        id="losers_chart",
                        figure=LosersPlotlyBarChart().render(losers, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),

            dbc.Col(
                _chart_section(
                    "Top Winners",
                    dcc.Graph(
                        id="winners_chart",
                        figure=WinnersPlotlyBarChart().render(winners, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),

            dbc.Col(
                _chart_section(
                    "Position Weight",
                    dcc.Graph(
                        id="position_weight_donut_chart",
                        figure=PositionWeightPlotlyDonutChart().render(position_weight_series, theme=theme),
                        config=_GRAPH_CONFIG,
                    ),
                ),
            ),

        ], className="mb-6 workspace-chart-grid", style={"gridTemplateColumns": "1fr 1fr 25%"}),

        html.Hr(className="tv-divider"),
        dbc.Row([
            dbc.Col(
                _chart_section(
                    "Today's Movers",
                    dcc.Graph(
                        id="daily_movers_chart",
                        figure=DailyMoversBarChart().render(daily_movers, theme=theme, x_col="daily_return"),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),
        ], className="mb-6 workspace-chart-grid"),

    ], id="tab-portfolio-content", className='workspace-wrapper')


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
            _chart_section("Price",
                dcc.Graph(
                    id="workspace-price-graph",
                    figure=PriceStructurePlotlyLineChart().render(asset_history, theme=theme),
                    config=_GRAPH_CONFIG,
                ),
            ),

            _chart_section("Asset Value",
                dcc.Graph(
                    id="workspace-value-graph",
                    figure=AssetValuePlotlyLineChart().render(asset_history, theme=theme),
                    config=_GRAPH_CONFIG,
                )
            ),

            _chart_section("Profit Range (30D)",
                dcc.Graph(
                    id="workspace-profit-range-graph",
                    figure=ProfitRangePlotlyLineChart().render(asset_history, theme=theme),
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

def risk_tab_content(view_model=None, theme="light"):
    if view_model is None:
        return _loading_placeholder("tab-risk-content", "Loading risk charts…")

    losers_pnl = view_model.get("losers_pnl", [])
    drawdown_series = view_model.get("portfolio_drawdown", {})
    profitability_data_vm = view_model.get("profitability")
    var_data = view_model.get("var_by_position", [])

    return html.Div([
        # ─────────────────────────────────────────────
        # Row: Drawdown + Profitability Donut
        # ─────────────────────────────────────────────
        dbc.Row([
            dbc.Col(
                _chart_section(
                    "Portfolio Drawdown",
                    dcc.Graph(
                        id="portfolio_drawdown_chart",
                        figure=PortfolioDrawdownPlotlyLineChart().render(drawdown_series, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),
            dbc.Col(
                _chart_section(
                    "Profit & Loss",
                    dcc.Graph(
                        id="profitability_donut_chart",
                        figure=PositionProfitabilityPlotlyDonutChart().render(profitability_data_vm, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
                width=4,
            ),
        ], className="mb-6 workspace-chart-grid"),

        # ─────────────────────────────────────────────
        # Row: Unprofitable Positions P&L
        # ─────────────────────────────────────────────
        html.Hr(className="tv-divider"),
        dbc.Row([
            dbc.Col(
                _chart_section(
                    "Unprofitable Positions P&L",
                    dcc.Graph(
                        id="losers_pnl_chart",
                        figure=LosersPnLPlotlyLineChart().render(losers_pnl, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),
        ], className="mb-6 workspace-chart-grid"),

        html.Hr(className="tv-divider"),
        dbc.Row([
            dbc.Col(
                _chart_section(
                    "Value at Risk by Position",
                    dcc.Graph(
                        id="var_by_position_chart",
                        figure=VaRBarChart().render(var_data, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),
        ], className="mb-6 workspace-chart-grid"),

    ], id="tab-risk-content", className='workspace-wrapper')


# ─────────────────────────────────────────────
# Opportunities tab content
# ─────────────────────────────────────────────

def opportunities_tab_content(view_model=None, theme="light"):
    if view_model is None:
        return _loading_placeholder("tab-opportunities-content", "Loading opportunities charts…")

    position_distribution = view_model.get("position_distribution", [])
    winners_pnl = view_model.get("winners_pnl", [])

    return html.Div([
        # ─────────────────────────────────────────────
        # Row: Position Performance Map
        # ─────────────────────────────────────────────
        dbc.Row([
            dbc.Col(
                _chart_section(
                    "Position Performance Map",
                    dcc.Graph(
                        id="portfolio_performance_map",
                        figure=PortfolioPerformanceScatterPlot().render(position_distribution, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
                className='workpspace-chart-performance-map',
            ),
        ], className="mb-6 workspace-chart-grid"),

        # ─────────────────────────────────────────────
        # Row: Profitable Positions P&L
        # ─────────────────────────────────────────────
        html.Hr(className="tv-divider"),
        dbc.Row([
            dbc.Col(
                _chart_section(
                    "Profitable Positions P&L",
                    dcc.Graph(
                        id="winners_pnl_chart",
                        figure=WinnersPnLPlotlyLineChart().render(winners_pnl, theme=theme),
                        config=_GRAPH_CONFIG,
                    )
                ),
            ),
        ], className="mb-6 workspace-chart-grid"),

    ], id="tab-opportunities-content", className='workspace-wrapper')


# ─────────────────────────────────────────────
# Asset Profile tab content
# ─────────────────────────────────────────────

def _summary_prop(label, value_id):
    return html.Div([
        html.Div(label, className="prop-label"),
        html.Div("—", id=value_id, className="prop-value"),
    ], className="profile-summary-prop")


def tags_tab_content():
    return html.Div([

        # ─────────────────────────────────────────────
        # Top — AWS-style summary card
        # ─────────────────────────────────────────────
        html.Div([
            html.Div("Asset Details", className="summary-card-header"),

            # Row 1: identity
            dbc.Row([
                dbc.Col(_summary_prop("Ticker", "profile-ticker"), width=2),
                dbc.Col(_summary_prop("Name", "profile-name"), width=3),
                dbc.Col(_summary_prop("Description", "profile-description"), width=4),
                dbc.Col(_summary_prop("First Seen", "profile-created"), width=2),
                dbc.Col(_summary_prop("Last Ingestion", "profile-last-ingestion"), width=1),
            ], className="g-3 mb-3"),

            html.Hr(className="tv-divider"),

            # Row 2: current classification values
            dbc.Row([
                dbc.Col(_summary_prop("Tags", "profile-summary-tags"), width=3),
                dbc.Col(_summary_prop("Category", "profile-summary-category"), width=3),
                dbc.Col(_summary_prop("Industry", "profile-summary-industry"), width=3),
                dbc.Col(_summary_prop("Sector", "profile-summary-sector"), width=3),
            ], className="g-3"),

        ], className="profile-summary-card mb-4"),

        # ─────────────────────────────────────────────
        # Bottom — accordion forms + single save
        # ─────────────────────────────────────────────
        dbc.Accordion([
            dbc.AccordionItem(
                dcc.Dropdown(
                    id="profile-tag-select",
                    placeholder="Select or search tag\u2026",
                    options=[],
                ),
                title="Tag",
                item_id="acc-tag",
            ),
            dbc.AccordionItem(
                dcc.Dropdown(
                    id="profile-category-select",
                    placeholder="Select or search category\u2026",
                    options=[],
                ),
                title="Categorizing Tag",
                item_id="acc-category",
            ),
            dbc.AccordionItem(
                dcc.Dropdown(
                    id="profile-industry-select",
                    placeholder="Select or search industry\u2026",
                    options=[],
                ),
                title="Industry",
                item_id="acc-industry",
            ),
            dbc.AccordionItem(
                dcc.Dropdown(
                    id="profile-sector-select",
                    placeholder="Select or search sector\u2026",
                    options=[],
                ),
                title="Sector",
                item_id="acc-sector",
            ),
        ], id="profile-accordion", always_open=True),

        html.Div([
            dbc.Button("Save", id="profile-save-btn", color="primary", size="sm", className="me-2"),
            html.Small("", id="profile-save-status", className="text-muted"),
        ], className="d-flex align-items-center mt-3"),

        # Hidden legacy IDs required by callbacks
        html.Div(id="profile-current-tags", style={"display": "none"}),
        html.Div(id="profile-tag-status", style={"display": "none"}),

    ], id="tab-tags-content")


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
            dbc.Tab(
                label="Asset Profile",
                tab_id="tab-tags",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=tags_tab_content(),
            ),
        ],
    )
