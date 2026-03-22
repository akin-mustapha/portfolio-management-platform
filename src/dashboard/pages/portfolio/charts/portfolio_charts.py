"""
Portfolio chart classes — re-exported from the implementation module.

To edit chart logic, open:
  pages/portfolio/components/charts.py

Classes:
  PortfolioPerformancePlotlyLineChart  — portfolio value over time
  PortfolioPNLPlotlyLineChart          — cumulative profit/loss
  PortfolioDrawdownPlotlyLineChart     — drawdown percentage
  PortfolioPerformanceScatterPlot      — risk/return scatter
  PortfolioFXAttributionDonutChart     — FX vs price return attribution
  PositionWeightPlotlyDonutChart       — allocation pie
  PositionProfitabilityPlotlyDonutChart — profit distribution
  WinnersPnLPlotlyLineChart            — top profitable positions
  LosersPnLPlotlyLineChart             — top unprofitable positions
  WinnersPlotlyBarChart                — winners bar chart
  LosersPlotlyBarChart                 — losers bar chart
  VaRBarChart                          — value at risk ranking

Helpers:
  _ranked_panel(data, sort_by, is_gain) — ranked row list
  daily_movers_table(data, n)           — today's movers table
  daily_change_sparkline(series, ...)   — inline sparkline figure
"""
from ..components.charts import (
    _apply_spike_config,
    _PnLPlotlyLineChart,
    _BaseRankedBarChart,
    _ranked_panel,
    WinnersPnLPlotlyLineChart,
    LosersPnLPlotlyLineChart,
    WinnersPlotlyBarChart,
    LosersPlotlyBarChart,
    VaRBarChart,
    PortfolioPerformanceScatterPlot,
    PositionWeightPlotlyDonutChart,
    PositionProfitabilityPlotlyDonutChart,
    PortfolioDrawdownPlotlyLineChart,
    PortfolioPerformancePlotlyLineChart,
    PortfolioPNLPlotlyLineChart,
    PortfolioFXAttributionDonutChart,
    daily_movers_table,
    daily_change_sparkline,
)

__all__ = [
    "_apply_spike_config",
    "_PnLPlotlyLineChart",
    "_BaseRankedBarChart",
    "_ranked_panel",
    "WinnersPnLPlotlyLineChart",
    "LosersPnLPlotlyLineChart",
    "WinnersPlotlyBarChart",
    "LosersPlotlyBarChart",
    "VaRBarChart",
    "PortfolioPerformanceScatterPlot",
    "PositionWeightPlotlyDonutChart",
    "PositionProfitabilityPlotlyDonutChart",
    "PortfolioDrawdownPlotlyLineChart",
    "PortfolioPerformancePlotlyLineChart",
    "PortfolioPNLPlotlyLineChart",
    "PortfolioFXAttributionDonutChart",
    "daily_movers_table",
    "daily_change_sparkline",
]
