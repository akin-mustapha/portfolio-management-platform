"""006_staging_asset_computed_metrics

Revision ID: 2200000000b6
Revises: 2200000000b5
Create Date: 2026-03-19

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2200000000b6"
down_revision: str | Sequence[str] | None = "2200000000b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE staging.asset_computed ADD COLUMN pnl_pct FLOAT")
    op.execute("ALTER TABLE staging.asset_computed ADD COLUMN var_95_1d FLOAT")
    op.execute("ALTER TABLE staging.asset_computed ADD COLUMN profit_range_30d FLOAT")
    op.execute("ALTER TABLE staging.asset_computed ADD COLUMN ma_crossover_signal FLOAT")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE staging.asset_computed DROP COLUMN pnl_pct")
    op.execute("ALTER TABLE staging.asset_computed DROP COLUMN var_95_1d")
    op.execute("ALTER TABLE staging.asset_computed DROP COLUMN profit_range_30d")
    op.execute("ALTER TABLE staging.asset_computed DROP COLUMN ma_crossover_signal")
