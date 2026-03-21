"""010_staging_computed_metrics_v2

Revision ID: 2200000000b10
Revises: 2200000000b9
Create Date: 2026-03-20

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2200000000b10'
down_revision: Union[str, Sequence[str], None] = '2200000000b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add position_weight_pct to asset_computed; portfolio_volatility_weighted to account_computed."""
    op.execute("ALTER TABLE staging.asset_computed ADD COLUMN position_weight_pct FLOAT")
    op.execute("ALTER TABLE staging.account_computed ADD COLUMN portfolio_volatility_weighted FLOAT")


def downgrade() -> None:
    op.execute("ALTER TABLE staging.asset_computed DROP COLUMN position_weight_pct")
    op.execute("ALTER TABLE staging.account_computed DROP COLUMN portfolio_volatility_weighted")
