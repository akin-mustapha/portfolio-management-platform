"""011_analytics_fact_technical_price_drawdown

Adds four price-based drawdown columns to `analytics.fact_technical`:
`price_drawdown_pct_{30,90,180,365}d`. These coexist with the existing
value-based `value_drawdown_pct_30d` column rather than replacing it —
the dashboard still reads the value-based column, and the price-based
family is consumed by the DCA automation script.

All four columns are nullable: a column is NULL until the ticker has
accumulated the full window of trading-day rows (gating handled in
staging.v_asset_metrics — see migration 015_staging_drawdown_windows).

Revision ID: 3300000000cb
Revises: 3300000000ca
Create Date: 2026-04-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3300000000cb"
down_revision: Union[str, Sequence[str], None] = "3300000000ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_NEW_COLUMNS = [
    "price_drawdown_pct_30d",
    "price_drawdown_pct_90d",
    "price_drawdown_pct_180d",
    "price_drawdown_pct_365d",
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
