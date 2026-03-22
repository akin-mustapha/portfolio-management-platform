"""
Asset comparison chart classes — re-exported from the implementation module.

To edit chart logic, open:
  pages/portfolio/components/asset_charts.py

Classes:
  PriceStructurePlotlyLineChart  — price comparison with reference line
  AssetValuePlotlyLineChart      — position value comparison
  ProfitRangePlotlyLineChart     — profit range (30D)
  RiskContextPlotlyLineChart     — risk metrics comparison
  DCABiasPlotlyLineChart         — dollar-cost averaging bias
  FXReturnAttributionDonutChart  — FX vs price return split per asset
"""
from ..components.asset_charts import (
    _hex_to_rgba,
    _apply_spike_config,
    _base_layout,
    PriceStructurePlotlyLineChart,
    AssetValuePlotlyLineChart,
    RiskContextPlotlyLineChart,
    DCABiasPlotlyLineChart,
    FXReturnAttributionDonutChart,
    ProfitRangePlotlyLineChart,
)

__all__ = [
    "_hex_to_rgba",
    "_apply_spike_config",
    "_base_layout",
    "PriceStructurePlotlyLineChart",
    "AssetValuePlotlyLineChart",
    "RiskContextPlotlyLineChart",
    "DCABiasPlotlyLineChart",
    "FXReturnAttributionDonutChart",
    "ProfitRangePlotlyLineChart",
]
