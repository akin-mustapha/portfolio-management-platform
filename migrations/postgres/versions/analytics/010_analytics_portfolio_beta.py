"""010_analytics_portfolio_beta

Adds portfolio_beta_weighted to fact_portfolio_daily — the weight-averaged
Beta of all positions, computed the same way as portfolio_volatility_weighted.

Revision ID: 3300000000ca
Revises: 3300000000c9
Create Date: 2026-04-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3300000000ca"
down_revision: Union[str, Sequence[str], None] = "3300000000c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "fact_portfolio_daily",
        sa.Column("portfolio_beta_weighted", sa.Numeric(10, 6), nullable=True),
        schema="analytics",
    )


def downgrade() -> None:
    op.drop_column("fact_portfolio_daily", "portfolio_beta_weighted", schema="analytics")
