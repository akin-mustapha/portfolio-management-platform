"""004_raw_fred_observations

Revision ID: 1100000000a4
Revises: 1100000000a3
Create Date: 2026-04-04

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1100000000a4'
down_revision: Union[str, Sequence[str], None] = '1100000000a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.fred_observations (
            id                  TEXT NOT NULL,
            series_id           VARCHAR(20) NOT NULL,
            ingested_date       DATE NOT NULL,
            ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
            observation_start   DATE NOT NULL,
            observations        JSONB NOT NULL,
            processed_at        TIMESTAMPTZ
        )
        PARTITION BY RANGE (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_fred_observations_ingested_date
        ON raw.fred_observations (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_fred_observations_series_id
        ON raw.fred_observations (series_id);

        CREATE INDEX IF NOT EXISTS idx_raw_fred_observations_processed_at
        ON raw.fred_observations (processed_at);
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS raw.fred_observations CASCADE")
