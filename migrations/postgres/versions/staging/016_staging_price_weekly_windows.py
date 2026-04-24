"""016_staging_price_weekly_windows

Adds 7-day and 14-day rolling price columns to staging.v_asset_metrics:

  recent_price_high_7d   — gated: NULL until 7 rows of history
  recent_price_low_7d    — ungated: best available within the window
  recent_price_high_14d  — gated: NULL until 14 rows of history
  recent_price_low_14d   — ungated: best available within the window

Lows are intentionally ungated — a partial-window low is still meaningful
for DCA context. Highs (and the drawdown derived from them) are gated so
the drawdown percentage is not artificially shallow when the window is short.

Revision ID: 2200000000b16
Revises: 2200000000b15
Create Date: 2026-04-24
"""
from typing import Sequence, Union

from alembic import op


revision: str = "2200000000b16"
down_revision: Union[str, Sequence[str], None] = "2200000000b15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_V_ASSET_METRICS = """
    CREATE MATERIALIZED VIEW staging.v_asset_metrics AS
    WITH deduped AS (
        SELECT
            id, ticker, snapshot_id, data_timestamp,
            value, cost, profit, price, avg_price, fx_impact,
            ROW_NUMBER() OVER (
                PARTITION BY ticker, data_timestamp::DATE
                ORDER BY data_timestamp DESC
            ) AS rn
        FROM staging.asset
    ),
    daily AS (
        SELECT
            id, ticker, snapshot_id, data_timestamp,
            value, cost, profit, price, avg_price, fx_impact,
            (price - LAG(price) OVER (PARTITION BY ticker ORDER BY data_timestamp))
            / NULLIF(LAG(price) OVER (PARTITION BY ticker ORDER BY data_timestamp), 0)
                AS daily_return
        FROM deduped
        WHERE rn = 1
    ),
    with_fred AS (
        SELECT
            d.*,
            COALESCE(rfr.daily_rfr, 0) AS daily_rfr,
            sp.sp500_daily_return
        FROM daily d
        LEFT JOIN staging.v_fred_rfr   rfr ON rfr.observation_date = d.data_timestamp::DATE
        LEFT JOIN staging.v_fred_sp500 sp  ON sp.observation_date  = d.data_timestamp::DATE
    )
    SELECT
        id, ticker, snapshot_id, data_timestamp,
        value, cost, profit, price, avg_price, fx_impact,
        daily_return,

        EXP(SUM(LN(1 + COALESCE(daily_return, 0))) OVER w_all) - 1
            AS cumulative_return,

        AVG(value) OVER w_20  AS value_ma_20d,
        AVG(value) OVER w_30  AS value_ma_30d,
        AVG(value) OVER w_50  AS value_ma_50d,
        AVG(price) OVER w_20  AS price_ma_20d,
        AVG(price) OVER w_50  AS price_ma_50d,

        STDDEV(daily_return) OVER w_20 AS volatility_20d,
        STDDEV(daily_return) OVER w_30 AS volatility_30d,
        STDDEV(daily_return) OVER w_50 AS volatility_50d,

        MAX(value)  OVER w_30 AS recent_value_high_30d,
        MIN(value)  OVER w_30 AS recent_value_low_30d,
        MAX(profit) OVER w_30 AS recent_profit_high_30d,
        MIN(profit) OVER w_30 AS recent_profit_low_30d,

        CASE WHEN COUNT(price) OVER w_7   = 7   THEN MAX(price) OVER w_7   END AS recent_price_high_7d,
        MIN(price) OVER w_7                                                     AS recent_price_low_7d,
        CASE WHEN COUNT(price) OVER w_14  = 14  THEN MAX(price) OVER w_14  END AS recent_price_high_14d,
        MIN(price) OVER w_14                                                    AS recent_price_low_14d,
        CASE WHEN COUNT(price) OVER w_30  = 30  THEN MAX(price) OVER w_30  END AS recent_price_high_30d,
        CASE WHEN COUNT(price) OVER w_90  = 90  THEN MAX(price) OVER w_90  END AS recent_price_high_90d,
        CASE WHEN COUNT(price) OVER w_180 = 180 THEN MAX(price) OVER w_180 END AS recent_price_high_180d,
        CASE WHEN COUNT(price) OVER w_365 = 365 THEN MAX(price) OVER w_365 END AS recent_price_high_365d,

        MAX(value) OVER (PARTITION BY ticker) AS value_high_alltime,
        MIN(value) OVER (PARTITION BY ticker) AS value_low_alltime,

        COVAR_POP(daily_return, sp500_daily_return) OVER w_60
        / NULLIF(VAR_POP(sp500_daily_return) OVER w_60, 0)
            AS beta_60d,

        AVG(daily_return - daily_rfr) OVER w_30
        / NULLIF(STDDEV_POP(daily_return) OVER w_30, 0)
        * SQRT(252)
            AS sharpe_ratio_30d
    FROM with_fred
    WINDOW
        w_all AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
        w_7   AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 6   PRECEDING AND CURRENT ROW),
        w_14  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 13  PRECEDING AND CURRENT ROW),
        w_20  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 19  PRECEDING AND CURRENT ROW),
        w_30  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 29  PRECEDING AND CURRENT ROW),
        w_50  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 49  PRECEDING AND CURRENT ROW),
        w_60  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 59  PRECEDING AND CURRENT ROW),
        w_90  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 89  PRECEDING AND CURRENT ROW),
        w_180 AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 179 PRECEDING AND CURRENT ROW),
        w_365 AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 364 PRECEDING AND CURRENT ROW)
"""

_V_ACCOUNT_METRICS = """
    CREATE MATERIALIZED VIEW staging.v_account_metrics AS
    WITH deduped AS (
        SELECT
            a.*,
            ROW_NUMBER() OVER (
                PARTITION BY data_timestamp::DATE
                ORDER BY data_timestamp DESC
            ) AS rn
        FROM staging.account a
    ),
    ranked AS (
        SELECT
            *,
            LAG(total_value) OVER (ORDER BY data_timestamp) AS prev_total_value,
            LAG(investments_total_cost + investments_unrealized_pnl)
                OVER (ORDER BY data_timestamp) AS prev_invested_value
        FROM deduped
        WHERE rn = 1
    ),
    with_fred AS (
        SELECT
            r.*,
            COALESCE(rfr.daily_rfr, 0)         AS daily_rfr,
            COALESCE(sp.sp500_daily_return, 0) AS sp500_daily_return,
            ((r.investments_total_cost + r.investments_unrealized_pnl)
                - COALESCE(r.prev_invested_value,
                           r.investments_total_cost + r.investments_unrealized_pnl))
                / NULLIF(r.prev_invested_value, 0) AS portfolio_daily_return
        FROM ranked r
        LEFT JOIN staging.v_fred_rfr   rfr ON rfr.observation_date = r.data_timestamp::DATE
        LEFT JOIN staging.v_fred_sp500 sp  ON sp.observation_date  = r.data_timestamp::DATE
    ),
    port_agg AS (
        SELECT
            am.snapshot_id,
            SUM(am.fx_impact) AS fx_impact_total,
            SUM(am.value / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0)
                * COALESCE(am.volatility_30d, 0)) AS portfolio_volatility_weighted,
            SUM(am.value / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0)
                * COALESCE(am.beta_60d, 0))       AS portfolio_beta_weighted
        FROM staging.v_asset_metrics am
        JOIN with_fred acc ON acc.snapshot_id = am.snapshot_id
        GROUP BY am.snapshot_id
    )
    SELECT
        wf.snapshot_id,
        wf.data_timestamp,
        wf.total_value,
        wf.investments_total_cost,
        wf.investments_unrealized_pnl,
        wf.investments_realized_pnl,
        wf.cash_available_to_trade,
        wf.cash_reserved_for_orders,
        wf.cash_in_pies,
        wf.prev_invested_value,
        wf.portfolio_daily_return,
        wf.sp500_daily_return          AS benchmark_return_daily,

        AVG(wf.portfolio_daily_return - wf.daily_rfr) OVER w_30
        / NULLIF(STDDEV_POP(wf.portfolio_daily_return) OVER w_30, 0)
        * SQRT(252)                    AS sharpe_ratio_30d,

        (EXP(SUM(LN(1 + COALESCE(wf.portfolio_daily_return, 0))) OVER w_30) - 1)
      - (EXP(SUM(LN(1 + COALESCE(wf.sp500_daily_return, 0)))     OVER w_30) - 1)
                                       AS portfolio_vs_benchmark_30d,

        pa.fx_impact_total,
        pa.portfolio_volatility_weighted,
        pa.portfolio_beta_weighted
    FROM with_fred wf
    LEFT JOIN port_agg pa ON pa.snapshot_id = wf.snapshot_id
    WINDOW
        w_30 AS (ORDER BY wf.data_timestamp ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
"""


def upgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_account_metrics CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_asset_metrics CASCADE")
    op.execute(_V_ASSET_METRICS)
    op.execute("CREATE UNIQUE INDEX ux_v_asset_metrics_ticker_ts ON staging.v_asset_metrics (ticker, data_timestamp)")
    op.execute("CREATE INDEX ix_v_asset_metrics_snapshot ON staging.v_asset_metrics (snapshot_id)")
    op.execute(_V_ACCOUNT_METRICS)
    op.execute("CREATE UNIQUE INDEX ux_v_account_metrics_snapshot ON staging.v_account_metrics (snapshot_id)")
    op.execute("CREATE INDEX ix_v_account_metrics_ts ON staging.v_account_metrics (data_timestamp)")


def downgrade() -> None:
    # Rolls back to the 015 view — remove 7d/14d columns, keep 30/90/180/365d
    _V_ASSET_METRICS_PREV = """
        CREATE MATERIALIZED VIEW staging.v_asset_metrics AS
        WITH deduped AS (
            SELECT
                id, ticker, snapshot_id, data_timestamp,
                value, cost, profit, price, avg_price, fx_impact,
                ROW_NUMBER() OVER (
                    PARTITION BY ticker, data_timestamp::DATE
                    ORDER BY data_timestamp DESC
                ) AS rn
            FROM staging.asset
        ),
        daily AS (
            SELECT
                id, ticker, snapshot_id, data_timestamp,
                value, cost, profit, price, avg_price, fx_impact,
                (price - LAG(price) OVER (PARTITION BY ticker ORDER BY data_timestamp))
                / NULLIF(LAG(price) OVER (PARTITION BY ticker ORDER BY data_timestamp), 0)
                    AS daily_return
            FROM deduped
            WHERE rn = 1
        ),
        with_fred AS (
            SELECT
                d.*,
                COALESCE(rfr.daily_rfr, 0) AS daily_rfr,
                sp.sp500_daily_return
            FROM daily d
            LEFT JOIN staging.v_fred_rfr   rfr ON rfr.observation_date = d.data_timestamp::DATE
            LEFT JOIN staging.v_fred_sp500 sp  ON sp.observation_date  = d.data_timestamp::DATE
        )
        SELECT
            id, ticker, snapshot_id, data_timestamp,
            value, cost, profit, price, avg_price, fx_impact,
            daily_return,
            EXP(SUM(LN(1 + COALESCE(daily_return, 0))) OVER w_all) - 1 AS cumulative_return,
            AVG(value) OVER w_20  AS value_ma_20d,
            AVG(value) OVER w_30  AS value_ma_30d,
            AVG(value) OVER w_50  AS value_ma_50d,
            AVG(price) OVER w_20  AS price_ma_20d,
            AVG(price) OVER w_50  AS price_ma_50d,
            STDDEV(daily_return) OVER w_20 AS volatility_20d,
            STDDEV(daily_return) OVER w_30 AS volatility_30d,
            STDDEV(daily_return) OVER w_50 AS volatility_50d,
            MAX(value)  OVER w_30 AS recent_value_high_30d,
            MIN(value)  OVER w_30 AS recent_value_low_30d,
            MAX(profit) OVER w_30 AS recent_profit_high_30d,
            MIN(profit) OVER w_30 AS recent_profit_low_30d,
            CASE WHEN COUNT(price) OVER w_30  = 30  THEN MAX(price) OVER w_30  END AS recent_price_high_30d,
            CASE WHEN COUNT(price) OVER w_90  = 90  THEN MAX(price) OVER w_90  END AS recent_price_high_90d,
            CASE WHEN COUNT(price) OVER w_180 = 180 THEN MAX(price) OVER w_180 END AS recent_price_high_180d,
            CASE WHEN COUNT(price) OVER w_365 = 365 THEN MAX(price) OVER w_365 END AS recent_price_high_365d,
            MAX(value) OVER (PARTITION BY ticker) AS value_high_alltime,
            MIN(value) OVER (PARTITION BY ticker) AS value_low_alltime,
            COVAR_POP(daily_return, sp500_daily_return) OVER w_60
            / NULLIF(VAR_POP(sp500_daily_return) OVER w_60, 0) AS beta_60d,
            AVG(daily_return - daily_rfr) OVER w_30
            / NULLIF(STDDEV_POP(daily_return) OVER w_30, 0)
            * SQRT(252) AS sharpe_ratio_30d
        FROM with_fred
        WINDOW
            w_all AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
            w_20  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 19  PRECEDING AND CURRENT ROW),
            w_30  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 29  PRECEDING AND CURRENT ROW),
            w_50  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 49  PRECEDING AND CURRENT ROW),
            w_60  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 59  PRECEDING AND CURRENT ROW),
            w_90  AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 89  PRECEDING AND CURRENT ROW),
            w_180 AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 179 PRECEDING AND CURRENT ROW),
            w_365 AS (PARTITION BY ticker ORDER BY data_timestamp ROWS BETWEEN 364 PRECEDING AND CURRENT ROW)
    """
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_account_metrics CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_asset_metrics CASCADE")
    op.execute(_V_ASSET_METRICS_PREV)
    op.execute("CREATE UNIQUE INDEX ux_v_asset_metrics_ticker_ts ON staging.v_asset_metrics (ticker, data_timestamp)")
    op.execute("CREATE INDEX ix_v_asset_metrics_snapshot ON staging.v_asset_metrics (snapshot_id)")
    op.execute(_V_ACCOUNT_METRICS)
    op.execute("CREATE UNIQUE INDEX ux_v_account_metrics_snapshot ON staging.v_account_metrics (snapshot_id)")
    op.execute("CREATE INDEX ix_v_account_metrics_ts ON staging.v_account_metrics (data_timestamp)")
