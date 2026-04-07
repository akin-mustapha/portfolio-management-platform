"""Risk tab — drawdown, P&L profitability, VaR, unprofitable positions."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..charts.portfolio_charts import (
    PortfolioDrawdownPlotlyLineChart,
    PositionProfitabilityPlotlyDonutChart,
    LosersPnLPlotlyLineChart,
    VaRBarChart,
)
from ..components.molecules.collapsible_section import collapsible_section
from ..components.organisms.secondary_kpi import secondary_kpi_row
from ._helpers import _GRAPH_CONFIG, _chart_section, _loading_placeholder


def risk_tab_content(view_model=None, theme="light", kpi_data=None):
    if view_model is None:
        return _loading_placeholder("tab-risk-content", "Loading risk charts…")

    losers_pnl = view_model.get("losers_pnl", [])
    drawdown_series = view_model.get("portfolio_drawdown", {})
    profitability_data = view_model.get("profitability")
    var_data = view_model.get("var_by_position", [])

    return html.Div(
        [
            # ── Portfolio Overview — collapsible ───────────────────────
            collapsible_section(
                section_id="risk-portfolio",
                title="Portfolio Overview",
                is_open=True,
                subheader=secondary_kpi_row(kpi_data, theme=theme),
                children=[
                    html.Hr(className="tv-divider"),
                    # Row 1: Drawdown + Profitability donut
                    dbc.Row(
                        [
                            dbc.Col(
                                _chart_section(
                                    "Portfolio Drawdown",
                                    dcc.Graph(
                                        id="portfolio_drawdown_chart",
                                        figure=PortfolioDrawdownPlotlyLineChart().render(
                                            drawdown_series, theme=theme
                                        ),
                                        config=_GRAPH_CONFIG,
                                    ),
                                )
                            ),
                            dbc.Col(
                                _chart_section(
                                    "Profit & Loss",
                                    dcc.Graph(
                                        id="profitability_donut_chart",
                                        figure=PositionProfitabilityPlotlyDonutChart().render(
                                            profitability_data, theme=theme
                                        ),
                                        config=_GRAPH_CONFIG,
                                    ),
                                )
                            ),
                        ],
                        className="mb-6 workspace-chart-grid",
                        style={"gridTemplateColumns": "1fr 30%"},
                    ),
                    html.Hr(className="tv-divider"),
                    # Row 2: Losers P&L + VaR
                    dbc.Row(
                        [
                            dbc.Col(
                                _chart_section(
                                    "Unprofitable Positions P&L",
                                    dcc.Graph(
                                        id="losers_pnl_chart",
                                        figure=LosersPnLPlotlyLineChart().render(
                                            losers_pnl, theme=theme
                                        ),
                                        config=_GRAPH_CONFIG,
                                    ),
                                )
                            ),
                            dbc.Col(
                                _chart_section(
                                    "Value at Risk by Position",
                                    dcc.Graph(
                                        id="var_by_position_chart",
                                        figure=VaRBarChart().render(
                                            var_data, theme=theme
                                        ),
                                        config=_GRAPH_CONFIG,
                                    ),
                                )
                            ),
                        ],
                        className="mb-6 workspace-chart-grid",
                        style={"gridTemplateColumns": "1fr 40%"},
                    ),
                ],
            ),
            # ── Asset detail — populated on row selection ──────────────
            html.Div(id="risk-asset-detail-sections"),
        ],
        className="workspace-wrapper",
    )
