from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccountGoldRecord(BaseModel):
    """
    Contract for a single portfolio row promoted from staging to analytics.gold.

    One record per pipeline run (daily snapshot). Validated before writing to
    fact_portfolio_daily. All computed fields are Optional — account_computed
    rows may have NULL values (e.g. daily_change requires a prior day's record).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # Keys
    date_id: int  # YYYYMMDD integer — FK: analytics.dim_date.id
    portfolio_id: UUID  # FK: analytics.dim_portfolio.id

    # Monetary snapshot (staging.account)
    total_value: float
    total_cost: float
    unrealized_pnl: float
    unrealized_pnl_pct: float | None = None  # null-safe: total_cost may be 0
    realized_pnl: float | None = None

    # Daily movement (staging.account_computed)
    daily_value_change_abs: float | None = None
    daily_value_change_pct: float | None = None

    # Cash positions (staging.account)
    cash_available: float | None = None
    cash_reserved: float | None = None
    cash_in_pies: float | None = None
    cash_deployment_ratio: float | None = None  # (total_value - cash_available) / total_value

    # Cross-asset aggregates
    fx_impact_total: float | None = None  # SUM(staging.asset.fx_impact)
    portfolio_volatility_weighted: float | None = None  # Σ(weight_i * volatility_30d_i)
    portfolio_beta_weighted: float | None = None  # Σ(weight_i * beta_60d_i)

    # FRED metrics (fact_portfolio_daily)
    sharpe_ratio_30d: float | None = None  # 30-day annualised portfolio Sharpe
    benchmark_return_daily: float | None = None  # SP500 daily return
    portfolio_vs_benchmark_30d: float | None = None  # 30d cumulative delta vs SP500
