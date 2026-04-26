"""009_staging_asset_quantity_in_pies

Revision ID: 2200000000b9
Revises: 2200000000b8
Create Date: 2026-03-20

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2200000000b9"
down_revision: str | Sequence[str] | None = "2200000000b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Promote quantity_in_pies from bronze to staging.asset."""
    op.execute("ALTER TABLE staging.asset ADD COLUMN quantity_in_pies FLOAT")


def downgrade() -> None:
    op.execute("ALTER TABLE staging.asset DROP COLUMN quantity_in_pies")
