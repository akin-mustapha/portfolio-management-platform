"""014_portfolio_raw_bronze_table

Revision ID: 4ce1cda63acb
Revises: 5df2e1b367ab
Create Date: 2026-02-16 00:14:00.448103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ce1cda63acb'
down_revision: Union[str, Sequence[str], None] = '5df2e1b367ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE SCHEMA IF NOT EXISTS raw")
    
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.portfolio (
        -- ID is needed to ensure idempotency
        id TEXT,
        payload JSONB NOT NULL,
        ingested_date DATE NOT NULL,
        ingested_timestamp TIMESTAMPTZ DEFAULT now()
        )
        PARTITION BY RANGE (ingested_date);
        
        
        CREATE INDEX IF NOT EXISTS idx_raw_portfolio_ingested_date
        ON raw.portfolio (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_portfolio_id
        ON raw.portfolio (id);
    """
    )
    
def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS raw.portfolio CASCADE")
    op.execute("DROP SCHEMA IF EXISTS raw CASCADE")
