"""017_staging_asset_sector_industry

Adds sector_id and industry_id columns to staging.asset so the silver pipeline
can populate them via the sector enrichment step (which joins portfolio.asset).

Both columns are nullable — ETFs and unmapped assets are left NULL.
Population is handled at runtime by SectorEnrichmentStep, not in this migration.

Revision ID: 2200000000b17
Revises: 2200000000b16
Create Date: 2026-04-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "2200000000b17"
down_revision: Union[str, None] = "2200000000b16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE staging.asset
            ADD COLUMN IF NOT EXISTS sector_id   uuid,
            ADD COLUMN IF NOT EXISTS industry_id uuid
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_asset_sector_id   ON staging.asset (sector_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_asset_industry_id ON staging.asset (industry_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS staging.ix_asset_industry_id")
    op.execute("DROP INDEX IF EXISTS staging.ix_asset_sector_id")
    op.execute("""
        ALTER TABLE staging.asset
            DROP COLUMN IF EXISTS industry_id,
            DROP COLUMN IF EXISTS sector_id
    """)
