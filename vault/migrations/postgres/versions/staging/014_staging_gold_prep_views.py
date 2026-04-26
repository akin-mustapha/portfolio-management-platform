"""014_staging_gold_prep_views

Revision ID: 2200000000b14
Revises: 2200000000b13
Create Date: 2026-04-18

Materialised views that consolidate the shared computation previously inlined in
the monolithic gold source query. Each view is refreshable CONCURRENTLY and
carries a unique index to satisfy that requirement.

Dependency order (refresh in this order):
    v_fred_rfr, v_fred_sp500  -> independent
    v_asset_metrics           -> depends on v_fred_rfr, v_fred_sp500
    v_account_metrics         -> depends on v_asset_metrics, v_fred_rfr, v_fred_sp500
"""

from collections.abc import Sequence

from alembic import op

revision: str = "2200000000b14"
down_revision: str | Sequence[str] | None = "2200000000b13"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE MATERIALIZED VIEW staging.v_fred_rfr AS
        SELECT
            observation_date,
            value / 100.0 / 252.0 AS daily_rfr
        FROM staging.fred_observation
        WHERE series_id = 'DTB3';

        CREATE UNIQUE INDEX ux_v_fred_rfr_date
        ON staging.v_fred_rfr (observation_date);
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW staging.v_fred_sp500 AS
        SELECT
            observation_date,
            (value - LAG(value) OVER (ORDER BY observation_date))
                / NULLIF(LAG(value) OVER (ORDER BY observation_date), 0)
                AS sp500_daily_return
        FROM staging.fred_observation
        WHERE series_id = 'SP500';

        CREATE UNIQUE INDEX ux_v_fred_sp500_date
        ON staging.v_fred_sp500 (observation_date);
    """)

    op.execute("""
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
            w_all AS (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ),
            w_20 AS (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
            ),
            w_30 AS (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ),
            w_50 AS (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
            ),
            w_60 AS (
                PARTITION BY ticker ORDER BY data_timestamp
                ROWS BETWEEN 59 PRECEDING AND CURRENT ROW
            );

        CREATE UNIQUE INDEX ux_v_asset_metrics_ticker_ts
        ON staging.v_asset_metrics (ticker, data_timestamp);

        CREATE INDEX ix_v_asset_metrics_snapshot
        ON staging.v_asset_metrics (snapshot_id);
    """)

    op.execute("""
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
                LAG(total_value) OVER (ORDER BY data_timestamp)
                    AS prev_total_value,
                LAG(investments_total_cost + investments_unrealized_pnl)
                    OVER (ORDER BY data_timestamp)
                    AS prev_invested_value
            FROM deduped
            WHERE rn = 1
        ),
        with_fred AS (
            SELECT
                r.*,
                COALESCE(rfr.daily_rfr, 0)         AS daily_rfr,
                COALESCE(sp.sp500_daily_return, 0) AS sp500_daily_return,
                ((r.investments_total_cost + r.investments_unrealized_pnl)
                    - COALESCE(
                        r.prev_invested_value,
                        r.investments_total_cost + r.investments_unrealized_pnl
                    ))
                    / NULLIF(r.prev_invested_value, 0) AS portfolio_daily_return
            FROM ranked r
            LEFT JOIN staging.v_fred_rfr   rfr ON rfr.observation_date = r.data_timestamp::DATE
            LEFT JOIN staging.v_fred_sp500 sp  ON sp.observation_date  = r.data_timestamp::DATE
        ),
        port_agg AS (
            SELECT
                am.snapshot_id,
                SUM(am.fx_impact) AS fx_impact_total,
                SUM(
                    am.value
                    / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0)
                    * COALESCE(am.volatility_30d, 0)
                ) AS portfolio_volatility_weighted,
                SUM(
                    am.value
                    / NULLIF(acc.investments_total_cost + acc.investments_unrealized_pnl, 0)
                    * COALESCE(am.beta_60d, 0)
                ) AS portfolio_beta_weighted
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
            w_30 AS (
                ORDER BY wf.data_timestamp
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            );

        CREATE UNIQUE INDEX ux_v_account_metrics_snapshot
        ON staging.v_account_metrics (snapshot_id);

        CREATE INDEX ix_v_account_metrics_ts
        ON staging.v_account_metrics (data_timestamp);
    """)


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_account_metrics CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_asset_metrics CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_fred_sp500 CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS staging.v_fred_rfr CASCADE")
