"""003_raw_unified_snapshot

Revision ID: 1100000000a3
Revises: 1100000000a2
Create Date: 2026-03-23

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1100000000a3'
down_revision: Union[str, Sequence[str], None] = '1100000000a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.t212_snapshot (
            id                  TEXT NOT NULL,
            ingested_date       DATE NOT NULL,
            ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
            account_data        JSONB NOT NULL,
            position_data       JSONB NOT NULL,
            processed_at        TIMESTAMPTZ
        )
        PARTITION BY RANGE (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_t212_snapshot_ingested_date
        ON raw.t212_snapshot (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_t212_snapshot_id
        ON raw.t212_snapshot (id);

        CREATE INDEX IF NOT EXISTS idx_raw_t212_snapshot_processed_at
        ON raw.t212_snapshot (processed_at);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS raw.t212_snapshot CASCADE")
