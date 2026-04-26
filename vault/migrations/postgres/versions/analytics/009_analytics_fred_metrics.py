"""009_analytics_fred_metrics

Adds Sharpe Ratio and Beta columns driven by FRED data (DTB3 + SP500).

fact_technical (asset-level):
  - beta_60d          — 60-day rolling Beta vs SP500
  - sharpe_ratio_30d  — 30-day annualised Sharpe ratio per asset

fact_portfolio_daily (portfolio-level):
  - sharpe_ratio_30d           — 30-day annualised portfolio Sharpe
  - benchmark_return_daily     — SP500 daily return for the same date
  - portfolio_vs_benchmark_30d — 30-day cumulative return delta (portfolio minus SP500)

Revision ID: 3300000000c9
Revises: 3300000000c8
Create Date: 2026-04-04

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3300000000c9"
down_revision: str | Sequence[str] | None = "3300000000c8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # fact_technical — asset-level FRED metrics
    for col in ["beta_60d", "sharpe_ratio_30d"]:
        op.add_column(
            "fact_technical",
            sa.Column(col, sa.Numeric(10, 6), nullable=True),
            schema="analytics",
        )

    # fact_portfolio_daily — portfolio-level FRED metrics
    for col in [
        "sharpe_ratio_30d",
        "benchmark_return_daily",
        "portfolio_vs_benchmark_30d",
    ]:
        op.add_column(
            "fact_portfolio_daily",
            sa.Column(col, sa.Numeric(10, 6), nullable=True),
            schema="analytics",
        )


def downgrade() -> None:
    for col in [
        "portfolio_vs_benchmark_30d",
        "benchmark_return_daily",
        "sharpe_ratio_30d",
    ]:
        op.drop_column("fact_portfolio_daily", col, schema="analytics")

    for col in ["sharpe_ratio_30d", "beta_60d"]:
        op.drop_column("fact_technical", col, schema="analytics")
