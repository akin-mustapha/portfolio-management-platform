"""002_raw_account

Revision ID: 1100000000a2
Revises: 1100000000a1
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1100000000a2'
down_revision: Union[str, Sequence[str], None] = '1100000000a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.account (
        -- ID is needed to ensure idempotency
        id TEXT,
        payload JSONB NOT NULL,
        ingested_date DATE NOT NULL,
        ingested_timestamp TIMESTAMPTZ DEFAULT now()
        )
        PARTITION BY RANGE (ingested_date);


        CREATE INDEX IF NOT EXISTS idx_raw_account_ingested_date
        ON raw.account (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_account_id
        ON raw.account (id);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS raw.account CASCADE")
