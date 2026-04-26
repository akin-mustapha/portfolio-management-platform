"""013_staging_fred_observation

Revision ID: 2200000000b13
Revises: 2200000000b12
Create Date: 2026-04-04

"""

from collections.abc import Sequence

from alembic import op

revision: str = "2200000000b13"
down_revision: str | Sequence[str] | None = "2200000000b12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS staging.fred_observation (
            id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            series_id         VARCHAR(20) NOT NULL,
            observation_date  DATE NOT NULL,
            value             NUMERIC(18, 6) NOT NULL,
            business_key      TEXT UNIQUE NOT NULL,
            ingested_date     DATE,
            created_timestamp TIMESTAMPTZ DEFAULT now(),
            updated_timestamp TIMESTAMPTZ DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_staging_fred_observation_series_date
        ON staging.fred_observation (series_id, observation_date DESC);

        CREATE INDEX IF NOT EXISTS idx_staging_fred_observation_business_key
        ON staging.fred_observation (business_key);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS staging.fred_observation CASCADE")
