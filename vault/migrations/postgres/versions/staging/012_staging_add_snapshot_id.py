"""012_staging_add_snapshot_id

Revision ID: 2200000000b12
Revises: 2200000000b11
Create Date: 2026-03-22

"""

from collections.abc import Sequence

from alembic import op

revision: str = "2200000000b12"
down_revision: str | Sequence[str] | None = "2200000000b11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE staging.asset ADD COLUMN snapshot_id TEXT NULL")
    op.execute("ALTER TABLE staging.account ADD COLUMN snapshot_id TEXT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE staging.asset DROP COLUMN snapshot_id")
    op.execute("ALTER TABLE staging.account DROP COLUMN snapshot_id")
