"""Valuation tab — portfolio value, P&L, position weight, movers."""
import dash_bootstrap_components as dbc
from dash import dcc, html

from ..charts.portfolio_charts import (
    _ranked_panel,
    PortfolioPerformancePlotlyLineChart,
    PortfolioPNLPlotlyLineChart,
    PositionWeightPlotlyDonutChart,
    PortfolioFXAttributionDonutChart,
    daily_movers_table,
)
from ..components.kpis import secondary_kpi_row
from ._helpers import _GRAPH_CONFIG, _chart_section, _loading_placeholder


def portfolio_tab_content(view_model=None, theme="light", kpi_data=None):
    if view_model is None:
        return _loading_placeholder("tab-portfolio-content", "Loading portfolio charts…")

    value_series          = view_model.get("portfolio_value_series", {})
    pnl_series            = view_model.get("portfolio_pnl_series", {})
    _position_weight_data  = view_model.get("position_weight_series", {})
    position_weight_series = _position_weight_data.get("series", [])
    position_weight_avg    = _position_weight_data.get("avg_weight_pct", 0)
    fx_attribution        = view_model.get("portfolio_fx_attribution", {})
    winners               = view_model.get("winners", [])
    losers                = view_model.get("losers", [])
    daily_movers          = view_model.get("daily_movers", [])

    return html.Div([

        # ── Portfolio Overview — collapsible ───────────────────────
        html.Div([
            html.Div(
                ["Portfolio Overview", html.Span("›", className="tv-chevron")],
                id="portfolio-section-header",
                className="tv-section-header tv-section-header--section",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),

            secondary_kpi_row(kpi_data, theme=theme),

            dbc.Collapse(
                id="portfolio-charts-collapse",
                is_open=False,
                children=[

                    # Row 1: Value + P&L
                    dbc.Row([
                        dbc.Col(_chart_section(
                            "Portfolio Value",
                            dcc.Graph(
                                id="value_chart",
                                figure=PortfolioPerformancePlotlyLineChart().render(value_series, theme=theme),
                                config=_GRAPH_CONFIG,
                            ),
                        )),
                        dbc.Col(_chart_section(
                            "Portfolio P&L",
                            dcc.Graph(
                                id="pnl_chart",
                                figure=PortfolioPNLPlotlyLineChart().render(pnl_series, theme=theme),
                                config=_GRAPH_CONFIG,
                            ),
                        )),
                    ], className="mb-6 workspace-chart-grid"),

                    html.Hr(className="tv-divider"),

                    # Row 2: Winners / Losers / Weight / FX Attribution
                    dbc.Row([
                        dbc.Col(html.Div([
                            html.Div("Top Losers", className="tv-section-header"),
                            html.Div(
                                id="losers-table",
                                children=_ranked_panel(losers, "profit", False),
                                className="movers-table-scroll",
                            ),
                        ])),
                        dbc.Col(html.Div([
                            html.Div("Top Winners", className="tv-section-header"),
                            html.Div(
                                id="winners-table",
                                children=_ranked_panel(winners, "profit", True),
                                className="movers-table-scroll",
                            ),
                        ])),
                        dbc.Col(_chart_section(
                            "Position Weight",
                            dcc.Graph(
                                id="position_weight_donut_chart",
                                figure=PositionWeightPlotlyDonutChart().render(position_weight_series, avg_weight=position_weight_avg, theme=theme),
                                config=_GRAPH_CONFIG,
                            ),
                        )),
                        dbc.Col(_chart_section(
                            "Return Attribution (FX vs Price)",
                            dcc.Graph(
                                id="portfolio_fx_attribution_chart",
                                figure=PortfolioFXAttributionDonutChart().render(fx_attribution, theme=theme),
                                config=_GRAPH_CONFIG,
                            ),
                        )),
                    ], className="mb-6 workspace-chart-grid", style={"gridTemplateColumns": "1fr 1fr 25% 25%"}),

                    html.Hr(className="tv-divider"),

                    # Row 3: Daily movers
                    html.Div([
                        html.Div([
                            html.Div("Today's Movers", className="tv-section-header"),
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

        # ── Asset detail — populated on row selection ──────────────
        html.Div(id="asset-detail-sections"),

    ], className="workspace-wrapper")
