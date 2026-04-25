"""012_staging_add_snapshot_id

Revision ID: 2200000000b12
Revises: 2200000000b11
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op


revision: str = '2200000000b12'
down_revision: Union[str, Sequence[str], None] = '2200000000b11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE staging.asset ADD COLUMN snapshot_id TEXT NULL")
    op.execute("ALTER TABLE staging.account ADD COLUMN snapshot_id TEXT NULL")

def downgrade() -> None:
    op.execute("ALTER TABLE staging.asset DROP COLUMN snapshot_id")
    op.execute("ALTER TABLE staging.account DROP COLUMN snapshot_id")
