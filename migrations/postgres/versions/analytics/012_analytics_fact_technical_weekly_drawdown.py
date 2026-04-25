"""012_analytics_fact_technical_weekly_drawdown

Adds 7-day and 14-day price high, low, and drawdown columns to
`analytics.fact_technical`, feeding the DCA automation script.

  recent_price_high_7d   NUMERIC NULL  — gated (NULL until 7 rows)
  recent_price_low_7d    NUMERIC NULL  — ungated (partial window ok)
  price_drawdown_pct_7d  NUMERIC NULL  — gated (NULL until 7 rows)
  recent_price_high_14d  NUMERIC NULL  — gated (NULL until 14 rows)
  recent_price_low_14d   NUMERIC NULL  — ungated (partial window ok)
  price_drawdown_pct_14d NUMERIC NULL  — gated (NULL until 14 rows)

Revision ID: 3300000000cc
Revises: 3300000000cb
Create Date: 2026-04-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3300000000cc"
down_revision: Union[str, Sequence[str], None] = "3300000000cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_NEW_COLUMNS = [
    "recent_price_high_7d",
    "recent_price_low_7d",
    "price_drawdown_pct_7d",
    "recent_price_high_14d",
    "recent_price_low_14d",
    "price_drawdown_pct_14d",
]


def upgrade() -> None:
    for col in _NEW_COLUMNS:
        op.add_column(
            "fact_technical",
            sa.Column(col, sa.Numeric, nullable=True),
            schema="analytics",
        )


def downgrade() -> None:
    for col in reversed(_NEW_COLUMNS):
        op.drop_column("fact_technical", col, schema="analytics")
