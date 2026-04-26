"""create portfolio_snapshot table

Revision ID: ae9169cd149e
Revises: 1268104d5702
Create Date: 2026-01-16 15:22:03.819626

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ae9169cd149e"
down_revision: str | Sequence[str] | None = "1268104d5702"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

"""
{
  "cash": {
    "availableToTrade": 0,
    "inPies": 0,
    "reservedForOrders": 0
  },
  "currency": "string",
  "id": 0,
  "investments": {
    "currentValue": 0,
    "realizedProfitLoss": 0,
    "totalCost": 0,
    "unrealizedProfitLoss": 0
  },
  "totalValue": 0
}
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "portfolio_snapshot",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("external_id", sa.Integer),
        sa.Column("data_date", sa.DateTime),
        sa.Column("currency", sa.String),
        sa.Column("current_value", sa.Float),
        sa.Column("total_value", sa.Float),
        sa.Column("total_cost", sa.Float),
        sa.Column("unrealized_profit", sa.Float),
        sa.Column("realized_profit", sa.Float),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("portfolio_snapshot")
