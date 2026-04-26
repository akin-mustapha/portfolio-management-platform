"""008_analytics_rename_columns

Renames ambiguous column names across four fact tables so that names reflect
what they measure:
  - ma_20d/30d/50d → value_ma_20d/30d/50d (AVG of position value, not price)
  - value_high/low → value_high_alltime/low_alltime (all-time, vs 30d windows)
  - pct_drawdown → value_drawdown_pct_30d (value-based, from 30d high)
  - ma_crossover_signal → value_ma_crossover_signal (uses value MAs)
  - daily_return/cumulative_return → daily_value_return/cumulative_value_return
  - daily_change_abs/pct → daily_value_change_abs/pct (portfolio total value)
Also adds price_ma_20d and price_ma_50d to fact_technical — these were already
computed in the pipeline SQL but dropped before loading.

Revision ID: 3300000000c8
Revises: 3300000000c7
Create Date: 2026-03-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3300000000c8"
down_revision: str | Sequence[str] | None = "3300000000c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # fact_technical — rename value MAs
    for old, new in [
        ("ma_20d", "value_ma_20d"),
        ("ma_30d", "value_ma_30d"),
        ("ma_50d", "value_ma_50d"),
        ("value_high", "value_high_alltime"),
        ("value_low", "value_low_alltime"),
        ("pct_drawdown", "value_drawdown_pct_30d"),
    ]:
        op.alter_column("fact_technical", old, new_column_name=new, schema="analytics")

    # fact_technical — add price MAs (were computed but not persisted)
    for col in ["price_ma_20d", "price_ma_50d"]:
        op.add_column(
            "fact_technical",
            sa.Column(col, sa.Numeric, nullable=True),
            schema="analytics",
        )

    # fact_signal
    op.alter_column(
        "fact_signal",
        "ma_crossover_signal",
        new_column_name="value_ma_crossover_signal",
        schema="analytics",
    )

    # fact_return
    for old, new in [
        ("daily_return", "daily_value_return"),
        ("cumulative_return", "cumulative_value_return"),
    ]:
        op.alter_column("fact_return", old, new_column_name=new, schema="analytics")

    # fact_portfolio_daily
    for old, new in [
        ("daily_change_abs", "daily_value_change_abs"),
        ("daily_change_pct", "daily_value_change_pct"),
    ]:
        op.alter_column("fact_portfolio_daily", old, new_column_name=new, schema="analytics")


def downgrade() -> None:
    # fact_portfolio_daily
    for old, new in [
        ("daily_value_change_abs", "daily_change_abs"),
        ("daily_value_change_pct", "daily_change_pct"),
    ]:
        op.alter_column("fact_portfolio_daily", old, new_column_name=new, schema="analytics")

    # fact_return
    for old, new in [
        ("daily_value_return", "daily_return"),
        ("cumulative_value_return", "cumulative_return"),
    ]:
        op.alter_column("fact_return", old, new_column_name=new, schema="analytics")

    # fact_signal
    op.alter_column(
        "fact_signal",
        "value_ma_crossover_signal",
        new_column_name="ma_crossover_signal",
        schema="analytics",
    )

    # fact_technical — drop added price MA columns
    for col in ["price_ma_50d", "price_ma_20d"]:
        op.drop_column("fact_technical", col, schema="analytics")

    # fact_technical — reverse renames
    for old, new in [
        ("value_ma_20d", "ma_20d"),
        ("value_ma_30d", "ma_30d"),
        ("value_ma_50d", "ma_50d"),
        ("value_high_alltime", "value_high"),
        ("value_low_alltime", "value_low"),
        ("value_drawdown_pct_30d", "pct_drawdown"),
    ]:
        op.alter_column("fact_technical", old, new_column_name=new, schema="analytics")
