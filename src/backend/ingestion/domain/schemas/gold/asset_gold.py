from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetGoldRecord(BaseModel):
    """
    Contract for a single asset row promoted from staging to the analytics gold layer.

    One record per asset per pipeline run. Validated before fan-out to fact tables.
    All metric fields are Optional — staging.asset_computed rows may have NULL values
    for assets that haven't accumulated enough history (e.g. MA 50D needs 50 days).
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    # Keys — required, drive all FK relationships
    date_id: int          # YYYYMMDD integer — FK: analytics.dim_date.id
    portfolio_id: UUID    # FK: analytics.dim_portfolio.id
    asset_id: UUID        # staging.asset.id = analytics.dim_asset.asset_id

    # Price (fact_price)
    price: float
    avg_price: float

    # Valuation (fact_valuation)
    value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_pct: Optional[float] = None   # null-safe: cost_basis may be 0
    realized_pnl: Optional[float] = None          # not available per-position from broker
    position_weight_pct: Optional[float] = None
    fx_impact: Optional[float] = None

    # Returns (fact_return)
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None

    # Technical / Risk (fact_technical)
    pct_drawdown: Optional[float] = None
    value_high: Optional[float] = None
    value_low: Optional[float] = None
    ma_20d: Optional[float] = None
    ma_30d: Optional[float] = None
    ma_50d: Optional[float] = None
    volatility_20d: Optional[float] = None
    volatility_30d: Optional[float] = None
    volatility_50d: Optional[float] = None
    var_95_1d: Optional[float] = None
    profit_range_30d: Optional[float] = None
    recent_profit_high_30d: Optional[float] = None
    recent_profit_low_30d: Optional[float] = None
    recent_value_high_30d: Optional[float] = None
    recent_value_low_30d: Optional[float] = None

    # Signals / Opportunities (fact_signal)
    dca_bias: Optional[float] = None
    ma_crossover_signal: Optional[float] = None   # ma_20d - ma_50d; positive = bullish
    price_above_ma_20d: Optional[bool] = None
    price_above_ma_50d: Optional[bool] = None
