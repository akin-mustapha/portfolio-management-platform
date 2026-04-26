"""create asset_metric table

Revision ID: 956823608e97
Revises: ae9169cd149e
Create Date: 2026-01-23 19:54:11.465917

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "956823608e97"
down_revision: str | Sequence[str] | None = "ae9169cd149e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "asset_metric",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("asset.id")),
        sa.Column("data_date", sa.DateTime),
        sa.Column("pct_drawdown", sa.Float),
        sa.Column("recent_high_30d", sa.Float),
        sa.Column("recent_low_30d", sa.Float),
        sa.Column("ma_30", sa.Float),
        sa.Column("norm_price_30d", sa.Float),
        sa.Column("volatility_30d", sa.Float),
        sa.Column("price_vs_ma_50", sa.Float),
        sa.Column("ma_50", sa.Float),
        sa.Column("dca_bias", sa.Float),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("asset_metric")
