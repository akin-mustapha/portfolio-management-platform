from uuid import UUID

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
    date_id: int  # YYYYMMDD integer — FK: analytics.dim_date.id
    portfolio_id: UUID  # FK: analytics.dim_portfolio.id
    asset_id: UUID  # staging.asset.id = analytics.dim_asset.asset_id

    # Price (fact_price)
    price: float
    avg_price: float

    # Valuation (fact_valuation)
    value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_pct: float | None = None  # null-safe: cost_basis may be 0
    realized_pnl: float | None = None  # not available per-position from broker
    position_weight_pct: float | None = None
    fx_impact: float | None = None

    # Returns (fact_return)
    daily_value_return: float | None = None
    cumulative_value_return: float | None = None

    # Technical / Risk (fact_technical)
    value_drawdown_pct_30d: float | None = None
    recent_price_high_7d: float | None = None
    recent_price_low_7d: float | None = None
    price_drawdown_pct_7d: float | None = None
    recent_price_high_14d: float | None = None
    recent_price_low_14d: float | None = None
    price_drawdown_pct_14d: float | None = None
    price_drawdown_pct_30d: float | None = None
    price_drawdown_pct_90d: float | None = None
    price_drawdown_pct_180d: float | None = None
    price_drawdown_pct_365d: float | None = None
    value_high_alltime: float | None = None
    value_low_alltime: float | None = None
    value_ma_20d: float | None = None
    value_ma_30d: float | None = None
    value_ma_50d: float | None = None
    price_ma_20d: float | None = None
    price_ma_50d: float | None = None
    volatility_20d: float | None = None
    volatility_30d: float | None = None
    volatility_50d: float | None = None
    var_95_1d: float | None = None
    profit_range_30d: float | None = None
    recent_profit_high_30d: float | None = None
    recent_profit_low_30d: float | None = None
    recent_value_high_30d: float | None = None
    recent_value_low_30d: float | None = None

    # FRED metrics (fact_technical)
    beta_60d: float | None = None  # 60-day rolling Beta vs SP500
    sharpe_ratio_30d: float | None = None  # 30-day annualised Sharpe ratio

    # Signals / Opportunities (fact_signal)
    dca_bias: float | None = None
    value_ma_crossover_signal: float | None = None  # value_ma_20d - value_ma_50d; positive = bullish
    price_above_ma_20d: bool | None = None
    price_above_ma_50d: bool | None = None
