"""009_bronze_storage

Revision ID: c0002396119d
Revises: b7f8e7f57901
Create Date: 2026-02-08 21:38:43.193417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c0002396119d'
down_revision: Union[str, Sequence[str], None] = 'b7f8e7f57901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")
    
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.asset (
        -- ID is needed to ensure idempotency
        id TEXT,
        payload JSONB NOT NULL,
        ingested_date DATE NOT NULL,
        ingested_timestamp TIMESTAMPTZ DEFAULT now()
        )
        PARTITION BY RANGE (ingested_date);
        
        
        CREATE INDEX IF NOT EXISTS idx_raw_asset_ingested_date
        ON raw.asset (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_asset_id
        ON raw.asset (id);
    """
    )
    
    


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS raw.asset CASCADE")
    op.execute("DROP SCHEMA IF EXISTS raw CASCADE")
