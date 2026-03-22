"""Opportunities tab — performance scatter, profitable positions P&L."""
import dash_bootstrap_components as dbc
from dash import dcc, html

from ..charts.portfolio_charts import (
    PortfolioPerformanceScatterPlot,
    WinnersPnLPlotlyLineChart,
)
from ..components.kpis import secondary_kpi_row
from ._helpers import _GRAPH_CONFIG, _chart_section, _loading_placeholder


def opportunities_tab_content(view_model=None, theme="light", kpi_data=None):
    if view_model is None:
        return _loading_placeholder("tab-opportunities-content", "Loading opportunities charts…")

    position_distribution = view_model.get("position_distribution", [])
    winners_pnl           = view_model.get("winners_pnl", [])

    return html.Div([

        # ── Portfolio Overview — collapsible ───────────────────────
        html.Div([
            html.Div(
                ["Portfolio Overview", html.Span("›", className="tv-chevron")],
                id="opportunities-portfolio-section-header",
                className="tv-section-header tv-section-header--section",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),

            secondary_kpi_row(kpi_data, theme=theme),

            dbc.Collapse(
                id="opportunities-portfolio-charts-collapse",
                is_open=True,
                children=[

                    html.Hr(className="tv-divider"),

                    # Row 1: Performance scatter + Winners P&L
                    dbc.Row([
                        dbc.Col(_chart_section(
                            "Position Performance Map",
                            dcc.Graph(
                                id="portfolio_performance_map",
                                figure=PortfolioPerformanceScatterPlot().render(position_distribution, theme=theme),
                                config=_GRAPH_CONFIG,
                            ),
                        )),
                        dbc.Col(_chart_section(
                            "Profitable Positions P&L",
                            dcc.Graph(
                                id="winners_pnl_chart",
                                figure=WinnersPnLPlotlyLineChart().render(winners_pnl, theme=theme),
                                config=_GRAPH_CONFIG,
                            ),
                        )),
                    ], className="mb-6 workspace-chart-grid", style={"gridTemplateColumns": "3fr 2fr"}),

                ],
            ),
        ], className="tv-section-container"),

        # ── Asset detail — populated on row selection ──────────────
        html.Div(id="opportunities-asset-detail-sections"),

    ], className="workspace-wrapper")
