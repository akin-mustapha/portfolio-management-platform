"""006_analytics_schema_fixes

Fixes applied:
- dim_date: UUID PK replaced with YYYYMMDD integer PK (human-readable, fast joins)
- dim_time: dropped (daily snapshot system, sub-daily granularity has no use)
- dim_portfolio, dim_tag: duplicate created_datetime column removed
- dim_asset_type, dim_industry, dim_sector: created_datetime replaced with created_timestamp
- All fact tables: sector_id, tag_id, asset_type_id made nullable (external/manual data not guaranteed)
- fact_price: OHLC columns dropped (broker API does not provide open/close/high/low)
- fact_return: return column renamed to daily_return (reserved keyword in Python/SQLAlchemy)
- fact_valuation: added cost_basis, unrealized_pnl_pct, realized_pnl, position_weight_pct, fx_impact
- fact_technical: added value_high, value_low, var_95_1d, profit_range_30d
- fact_signal: added ma_crossover_signal, price_above_ma_20d, price_above_ma_50d
- All fact tables: unique constraint on (date_id, asset_id) to prevent duplicate daily rows
- fact_cashflow: dropped — cost_basis belongs in fact_valuation, no separate table needed
- NEW: fact_portfolio_daily — portfolio-wide daily snapshot table

Revision ID: 3300000000c6
Revises: 3300000000c5
Create Date: 2026-03-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "3300000000c6"
down_revision: Union[str, Sequence[str], None] = "3300000000c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # Step 1: Drop all fact tables — gold layer has no pipeline writing to it
    # yet, so these are empty. Dropping is cleaner than a chain of ALTER TABLEs.
    # -------------------------------------------------------------------------
    op.drop_table("fact_return", schema="analytics")
    op.drop_table("fact_cashflow", schema="analytics")
    op.drop_table("fact_valuation", schema="analytics")
    op.drop_table("fact_signal", schema="analytics")
    op.drop_table("fact_technical", schema="analytics")
    op.drop_table("fact_price", schema="analytics")

    # -------------------------------------------------------------------------
    # Step 2: Rebuild dim_date with YYYYMMDD integer PK
    # Truncate first (populated by 005), then replace the UUID PK with an
    # integer so the key is self-documenting and joins are faster.
    # -------------------------------------------------------------------------
    op.execute("TRUNCATE analytics.dim_date")
    op.execute("ALTER TABLE analytics.dim_date DROP CONSTRAINT dim_date_pkey")
    op.execute("ALTER TABLE analytics.dim_date DROP COLUMN id")
    op.execute("ALTER TABLE analytics.dim_date ADD COLUMN id INTEGER")
    op.execute("ALTER TABLE analytics.dim_date ADD PRIMARY KEY (id)")

    op.execute("""
        INSERT INTO analytics.dim_date (
            id,
            date,
            year,
            quarter,
            month,
            month_name,
            day_of_month,
            day_of_week,
            day_name,
            is_weekend,
            is_month_start,
            is_month_end,
            is_year_start,
            is_year_end
        )
        SELECT
            TO_CHAR(d, 'YYYYMMDD')::INTEGER             AS id,
            d::date                                      AS date,
            EXTRACT(YEAR FROM d)::int                    AS year,
            EXTRACT(QUARTER FROM d)::int                 AS quarter,
            EXTRACT(MONTH FROM d)::int                   AS month,
            TO_CHAR(d, 'Month')                          AS month_name,
            EXTRACT(DAY FROM d)::int                     AS day_of_month,
            EXTRACT(DOW FROM d)::int                     AS day_of_week,
            TO_CHAR(d, 'Day')                            AS day_name,
            EXTRACT(DOW FROM d) IN (0, 6)                AS is_weekend,
            d = date_trunc('month', d)::date             AS is_month_start,
            d = (date_trunc('month', d)
                + interval '1 month - 1 day')::date     AS is_month_end,
            d = date_trunc('year', d)::date              AS is_year_start,
            d = (date_trunc('year', d)
                + interval '1 year - 1 day')::date      AS is_year_end
        FROM generate_series(
            '2000-01-01'::date,
            '2035-12-31'::date,
            interval '1 day'
        ) AS d
    """)

    # -------------------------------------------------------------------------
    # Step 3: Drop dim_time — daily snapshot pipeline has no use for it
    # -------------------------------------------------------------------------
    op.drop_table("dim_time", schema="analytics")

    # -------------------------------------------------------------------------
    # Step 4: Clean up duplicate timestamp columns on dimension tables
    # dim_portfolio, dim_tag had both created_datetime + created_timestamp
    # dim_asset_type, dim_industry, dim_sector had created_datetime but no
    # created_timestamp
    # -------------------------------------------------------------------------
    op.drop_column("dim_portfolio", "created_datetime", schema="analytics")
    op.drop_column("dim_tag", "created_datetime", schema="analytics")

    op.drop_column("dim_asset_type", "created_datetime", schema="analytics")
    op.add_column(
        "dim_asset_type",
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="analytics",
    )

    op.drop_column("dim_industry", "created_datetime", schema="analytics")
    op.add_column(
        "dim_industry",
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="analytics",
    )

    op.drop_column("dim_sector", "created_datetime", schema="analytics")
    op.add_column(
        "dim_sector",
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="analytics",
    )

    # -------------------------------------------------------------------------
    # Step 5: Re-create fact tables (improved)
    # Common FK pattern across all position-level facts:
    #   date_id    INTEGER  NOT NULL → dim_date.id  (YYYYMMDD)
    #   asset_id   UUID     NOT NULL → dim_asset.asset_id
    #   portfolio_id UUID   NOT NULL → dim_portfolio.id
    #   sector_id  UUID     NULL     → dim_sector.id (external data, not always known)
    #   tag_id     UUID     NULL     → dim_tag.id    (manually maintained)
    #   asset_type_id UUID  NULL     → dim_asset_type.id
    # -------------------------------------------------------------------------

    # -- fact_price -----------------------------------------------------------
    # Broker API delivers a snapshot price only — no OHLC.
    # open_price, close_price, high, low removed.
    op.create_table(
        "fact_price",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", sa.Integer, sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=True),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=True),
        sa.Column("price", sa.Numeric, nullable=False),
        sa.Column("avg_price", sa.Numeric, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("date_id", "asset_id", name="uq_fact_price_date_asset"),
        schema="analytics",
    )

    # -- fact_valuation -------------------------------------------------------
    # Per-position monetary snapshot. Includes weight and FX drag so the
    # Portfolio tab can rank positions and sum FX impact without joins.
    op.create_table(
        "fact_valuation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", sa.Integer, sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=True),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=True),
        sa.Column("value", sa.Numeric, nullable=False),
        sa.Column("cost_basis", sa.Numeric, nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric, nullable=False),
        sa.Column("unrealized_pnl_pct", sa.Numeric, nullable=True),    # null-safe: cost_basis could be 0
        sa.Column("realized_pnl", sa.Numeric, nullable=True),
        sa.Column("position_weight_pct", sa.Numeric, nullable=True),   # value / portfolio total_value
        sa.Column("fx_impact", sa.Numeric, nullable=True),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("date_id", "asset_id", name="uq_fact_valuation_date_asset"),
        schema="analytics",
    )

    # -- fact_return ----------------------------------------------------------
    # "return" renamed to daily_return — Python reserved keyword.
    op.create_table(
        "fact_return",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", sa.Integer, sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=True),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=True),
        sa.Column("daily_return", sa.Numeric, nullable=True),
        sa.Column("cumulative_return", sa.Numeric, nullable=True),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("date_id", "asset_id", name="uq_fact_return_date_asset"),
        schema="analytics",
    )

    # -- fact_technical -------------------------------------------------------
    # Risk metrics per position. Includes VaR and profit range so the Risk tab
    # can be served from this table alone.
    op.create_table(
        "fact_technical",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", sa.Integer, sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=True),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=True),
        sa.Column("pct_drawdown", sa.Numeric, nullable=True),
        sa.Column("value_high", sa.Numeric, nullable=True),            # all-time high position value
        sa.Column("value_low", sa.Numeric, nullable=True),             # all-time low position value
        sa.Column("ma_20d", sa.Numeric, nullable=True),
        sa.Column("ma_30d", sa.Numeric, nullable=True),
        sa.Column("ma_50d", sa.Numeric, nullable=True),
        sa.Column("volatility_20d", sa.Numeric, nullable=True),
        sa.Column("volatility_30d", sa.Numeric, nullable=True),
        sa.Column("volatility_50d", sa.Numeric, nullable=True),
        sa.Column("var_95_1d", sa.Numeric, nullable=True),             # volatility_30d * value * 1.65
        sa.Column("profit_range_30d", sa.Numeric, nullable=True),      # recent_profit_high_30d - recent_profit_low_30d
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("date_id", "asset_id", name="uq_fact_technical_date_asset"),
        schema="analytics",
    )

    # -- fact_signal ----------------------------------------------------------
    # Entry/opportunity signals per position. Drives the Opportunities tab.
    op.create_table(
        "fact_signal",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", sa.Integer, sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=True),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=True),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=True),
        sa.Column("dca_bias", sa.Numeric, nullable=True),              # price / avg_price; <1 = below avg cost
        sa.Column("ma_crossover_signal", sa.Numeric, nullable=True),   # ma_20d - ma_50d; positive = bullish
        sa.Column("price_above_ma_20d", sa.Boolean, nullable=True),    # price > ma_20d
        sa.Column("price_above_ma_50d", sa.Boolean, nullable=True),    # price > ma_50d
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("date_id", "asset_id", name="uq_fact_signal_date_asset"),
        schema="analytics",
    )

    # -- fact_portfolio_daily -------------------------------------------------
    # Portfolio-wide daily snapshot. One row per day. Enables daily delta,
    # cash deployment ratio, weighted volatility, and max drawdown over time.
    # No asset_id dimension — this is account-level, not position-level.
    op.create_table(
        "fact_portfolio_daily",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", sa.Integer, sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("total_value", sa.Numeric, nullable=False),
        sa.Column("total_cost", sa.Numeric, nullable=False),
        sa.Column("unrealized_pnl", sa.Numeric, nullable=False),
        sa.Column("unrealized_pnl_pct", sa.Numeric, nullable=True),
        sa.Column("realized_pnl", sa.Numeric, nullable=True),
        sa.Column("daily_change_abs", sa.Numeric, nullable=True),      # total_value(T) - total_value(T-1)
        sa.Column("daily_change_pct", sa.Numeric, nullable=True),      # daily_change_abs / total_value(T-1)
        sa.Column("cash_available", sa.Numeric, nullable=True),
        sa.Column("cash_reserved", sa.Numeric, nullable=True),
        sa.Column("cash_in_pies", sa.Numeric, nullable=True),
        sa.Column("cash_deployment_ratio", sa.Numeric, nullable=True), # (total_value - cash_available) / total_value
        sa.Column("fx_impact_total", sa.Numeric, nullable=True),       # SUM(fx_impact) across all positions
        sa.Column("portfolio_volatility_weighted", sa.Numeric, nullable=True),  # Σ(weight_i * volatility_30d_i)
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("date_id", "portfolio_id", name="uq_fact_portfolio_daily_date_portfolio"),
        schema="analytics",
    )


def downgrade() -> None:
    op.drop_table("fact_portfolio_daily", schema="analytics")
    op.drop_table("fact_signal", schema="analytics")
    op.drop_table("fact_technical", schema="analytics")
    op.drop_table("fact_return", schema="analytics")
    op.drop_table("fact_valuation", schema="analytics")
    op.drop_table("fact_price", schema="analytics")

    # Restore dim_date to UUID PK (reverses the integer PK change)
    op.execute("TRUNCATE analytics.dim_date")
    op.execute("ALTER TABLE analytics.dim_date DROP CONSTRAINT dim_date_pkey")
    op.execute("ALTER TABLE analytics.dim_date DROP COLUMN id")
    op.execute(
        "ALTER TABLE analytics.dim_date ADD COLUMN id UUID DEFAULT gen_random_uuid()"
    )
    op.execute("ALTER TABLE analytics.dim_date ADD PRIMARY KEY (id)")
    op.execute("""
        INSERT INTO analytics.dim_date (
            date, year, quarter, month, month_name, day_of_month,
            day_of_week, day_name, is_weekend, is_month_start, is_month_end,
            is_year_start, is_year_end
        )
        SELECT
            d::date,
            EXTRACT(YEAR FROM d)::int,
            EXTRACT(QUARTER FROM d)::int,
            EXTRACT(MONTH FROM d)::int,
            TO_CHAR(d, 'Month'),
            EXTRACT(DAY FROM d)::int,
            EXTRACT(DOW FROM d)::int,
            TO_CHAR(d, 'Day'),
            EXTRACT(DOW FROM d) IN (0, 6),
            d = date_trunc('month', d)::date,
            d = (date_trunc('month', d) + interval '1 month - 1 day')::date,
            d = date_trunc('year', d)::date,
            d = (date_trunc('year', d) + interval '1 year - 1 day')::date
        FROM generate_series('2000-01-01'::date, '2035-12-31'::date, interval '1 day') AS d
    """)

    # Restore dim_time
    op.create_table(
        "dim_time",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("time", sa.Time, nullable=False, unique=True),
        sa.Column("hour", sa.Integer, nullable=False),
        sa.Column("minute", sa.Integer, nullable=False),
        sa.Column("second", sa.Integer, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=True),
        schema="analytics",
    )
    op.execute("""
        INSERT INTO analytics.dim_time (time, hour, minute, second)
        SELECT gs::time, EXTRACT(HOUR FROM gs), EXTRACT(MINUTE FROM gs), EXTRACT(SECOND FROM gs)
        FROM generate_series('2000-01-01 00:00:00'::timestamp, '2000-01-01 23:59:00'::timestamp, interval '1 minute') AS gs
    """)

    # Restore dimension duplicate columns
    op.add_column("dim_portfolio", sa.Column("created_datetime", sa.DateTime(timezone=True), nullable=True), schema="analytics")
    op.add_column("dim_tag", sa.Column("created_datetime", sa.DateTime(timezone=True), nullable=True), schema="analytics")

    op.drop_column("dim_asset_type", "created_timestamp", schema="analytics")
    op.add_column("dim_asset_type", sa.Column("created_datetime", sa.DateTime(timezone=True), nullable=True), schema="analytics")

    op.drop_column("dim_industry", "created_timestamp", schema="analytics")
    op.add_column("dim_industry", sa.Column("created_datetime", sa.DateTime(timezone=True), nullable=True), schema="analytics")

    op.drop_column("dim_sector", "created_timestamp", schema="analytics")
    op.add_column("dim_sector", sa.Column("created_datetime", sa.DateTime(timezone=True), nullable=True), schema="analytics")

    # Restore original fact tables (pre-fix state)
    op.create_table(
        "fact_price",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("average_price", sa.Float, nullable=False),
        sa.Column("open_price", sa.Float, nullable=False),
        sa.Column("close_price", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )
    op.create_table(
        "fact_technical",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("pct_drawdown", sa.Float, nullable=False),
        sa.Column("ma_20d", sa.Float, nullable=False),
        sa.Column("ma_30d", sa.Float, nullable=False),
        sa.Column("ma_50d", sa.Float, nullable=False),
        sa.Column("volatility_20d", sa.Float, nullable=False),
        sa.Column("volatility_30d", sa.Float, nullable=False),
        sa.Column("volatility_50d", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )
    op.create_table(
        "fact_signal",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("dca_bias", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )
    op.create_table(
        "fact_valuation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("unrealized_pnl", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )
    op.create_table(
        "fact_return",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("return", sa.Float, nullable=False),
        sa.Column("cumulative_return", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )
