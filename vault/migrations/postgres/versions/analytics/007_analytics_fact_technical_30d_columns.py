"""007_analytics_fact_technical_30d_columns

Adds 4 rolling 30D columns to fact_technical that the dashboard asset table
and Valuation tab consume. These were available in staging.asset_computed but
were omitted from the gold schema.

Revision ID: 3300000000c7
Revises: 3300000000c6
Create Date: 2026-03-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3300000000c7"
down_revision: str | Sequence[str] | None = "3300000000c6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    for col in [
        "recent_profit_high_30d",
        "recent_profit_low_30d",
        "recent_value_high_30d",
        "recent_value_low_30d",
    ]:
        op.add_column(
            "fact_technical",
            sa.Column(col, sa.Numeric, nullable=True),
            schema="analytics",
        )


def downgrade() -> None:
    for col in [
        "recent_value_low_30d",
        "recent_value_high_30d",
        "recent_profit_low_30d",
        "recent_profit_high_30d",
    ]:
        op.drop_column("fact_technical", col, schema="analytics")
