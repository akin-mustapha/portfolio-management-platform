import dash_bootstrap_components as dbc
from dash import dcc, html

from .charts import (
    _ranked_panel,
    PortfolioPerformancePlotlyLineChart,
    PortfolioPNLPlotlyLineChart,
    PositionWeightPlotlyDonutChart,
    PortfolioPerformanceScatterPlot,
    WinnersPnLPlotlyLineChart,
    LosersPnLPlotlyLineChart,
    PortfolioDrawdownPlotlyLineChart,
    PositionProfitabilityPlotlyDonutChart,
    VaRBarChart,
    daily_movers_table,
)

_GRAPH_CONFIG = {"displayModeBar": False}


def _chart_section(title, chart):
    return html.Div([
        html.Div(title, className="tv-section-header"),
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
        # Portfolio section — collapsible
        # ─────────────────────────────────────────────
        html.Div([
            html.Div(
                ["Portfolio Overview", html.Span("›", className="tv-chevron")],
                id="portfolio-section-header",
                className="tv-section-header tv-section-header--section",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),

            dbc.Collapse(
                id="portfolio-charts-collapse",
                is_open=False,
                children=[
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

                    html.Hr(className="tv-divider"),
                    dbc.Row([

                        dbc.Col(
                            html.Div([
                                html.Div("Top Losers", className="tv-section-header"),
                                html.Div(
                                    id="losers-table",
                                    children=_ranked_panel(losers, "profit", False),
                                    className="movers-table-scroll",
                                ),
                            ]),
                        ),

                        dbc.Col(
                            html.Div([
                                html.Div("Top Winners", className="tv-section-header"),
                                html.Div(
                                    id="winners-table",
                                    children=_ranked_panel(winners, "profit", True),
                                    className="movers-table-scroll",
                                ),
                            ]),
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
                    html.Div([
                        html.Div([
                            html.Div("Today's Movers", className="tv-section-header", style={"padding": "12px 0 8px"}),
                            dbc.Select(
                                id="daily-movers-n-dropdown",
                                options=[{"label": f"Top {n}", "value": n} for n in range(5, 31, 5)],
                                value=5,
                                className="movers-n-dropdown",
                            ),
                        ], className="movers-header-row"),
                        html.Div(
                            id="daily-movers-table",
                            children=daily_movers_table(daily_movers, n=5),
                            className="movers-table-scroll",
                        ),
                    ], className="mb-6"),
                ],
            ),
        ], className="tv-section-container"),

        # ─────────────────────────────────────────────
        # Asset detail — populated dynamically on row selection
        # ─────────────────────────────────────────────
        html.Div(id="asset-detail-sections"),

    ], id="tab-portfolio-content", className='workspace-wrapper')


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
        # Portfolio overview — collapsible
        # ─────────────────────────────────────────────
        html.Div(
            ["Portfolio Overview", html.Span("›", className="tv-chevron")],
            id="risk-portfolio-section-header",
            className="tv-section-header",
            n_clicks=0,
            style={"cursor": "pointer"},
        ),

        dbc.Collapse(
            id="risk-portfolio-charts-collapse",
            is_open=True,
            children=[
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
            ],
        ),

        # ─────────────────────────────────────────────
        # Asset detail — populated dynamically on row selection
        # ─────────────────────────────────────────────
        html.Div(id="risk-asset-detail-sections"),

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
        # Portfolio overview — collapsible
        # ─────────────────────────────────────────────
        html.Div(
            ["Portfolio Overview", html.Span("›", className="tv-chevron")],
            id="opportunities-portfolio-section-header",
            className="tv-section-header",
            n_clicks=0,
            style={"cursor": "pointer"},
        ),

        dbc.Collapse(
            id="opportunities-portfolio-charts-collapse",
            is_open=True,
            children=[
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
            ],
        ),

        # ─────────────────────────────────────────────
        # Asset detail — populated dynamically on row selection
        # ─────────────────────────────────────────────
        html.Div(id="opportunities-asset-detail-sections"),

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
                label="Valuation",
                tab_id="tab-portfolio",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=portfolio_tab_content(view_model, theme),
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
