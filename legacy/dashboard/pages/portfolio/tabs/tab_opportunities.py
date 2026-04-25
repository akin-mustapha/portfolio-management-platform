"""Opportunities tab — performance scatter, profitable positions P&L."""

from dash import dcc, html

from ..charts.portfolio_charts import (
    PortfolioPerformanceScatterPlot,
    WinnersPnLPlotlyLineChart,
)
from ..components.molecules.collapsible_section import collapsible_section
from ..components.organisms.secondary_kpi import secondary_kpi_row
from ._helpers import _GRAPH_CONFIG, _chart_section, _loading_placeholder


def opportunities_tab_content(view_model=None, theme="light", kpi_data=None):
    if view_model is None:
        return _loading_placeholder(
            "tab-opportunities-content", "Loading opportunities charts…"
        )

    currency_symbol = (kpi_data or {}).get("currency_symbol", "")
    position_distribution = view_model.get("position_distribution", [])
    winners_pnl = view_model.get("winners_pnl", [])

    return html.Div(
        [
            # ── Portfolio Overview — collapsible ───────────────────────
            collapsible_section(
                section_id="opportunities-portfolio",
                title="Portfolio Overview",
                is_open=True,
                subheader=secondary_kpi_row(kpi_data, theme=theme),
                children=[
                    html.Hr(className="tv-divider"),
                    # Row 1: Performance scatter + Winners P&L
                    html.Div(
                        _chart_section(
                            "Position Performance Map",
                            dcc.Graph(
                                id="portfolio_performance_map",
                                figure=PortfolioPerformanceScatterPlot().render(
                                    position_distribution,
                                    theme=theme,
                                    currency=currency_symbol,
                                ),
                                config=_GRAPH_CONFIG,
                            ),
                        )
                    ),
                    html.Div(
                        _chart_section(
                            "Profitable Positions P&L",
                            dcc.Graph(
                                id="winners_pnl_chart",
                                figure=WinnersPnLPlotlyLineChart().render(
                                    winners_pnl, theme=theme
                                ),
                                config=_GRAPH_CONFIG,
                            ),
                        )
                    ),
                ],
            ),
            # ── Asset detail — populated on row selection ──────────────
            # DISABLE
            # html.Div(id="opportunities-asset-detail-sections"),
        ],
        className="workspace-wrapper",
    )
