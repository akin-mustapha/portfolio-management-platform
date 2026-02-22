"""017_portfolio_service_pmp_59

Revision ID: 3f8f7fe34497
Revises: 192a2efb33f5
Create Date: 2026-02-21 23:43:29.469328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f8f7fe34497'
down_revision: Union[str, Sequence[str], None] = '192a2efb33f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
                
        ALTER TABLE portfolio.industry
        ADD COLUMN is_active Boolean NOT NULL DEFAULT(True);
                
        ALTER TABLE portfolio.industry_history
        ADD COLUMN is_active Boolean NOT NULL DEFAULT(True);
        
        
        ALTER TABLE portfolio.sector
        ADD COLUMN is_active Boolean NOT NULL DEFAULT(True);
        
        ALTER TABLE portfolio.sector_history
        ADD COLUMN is_active Boolean NOT NULL DEFAULT(True);
        
        DROP TABLE IF EXISTS portfolio.asset;
        DROP TABLE IF EXISTS portfolio.asset_v2;
        CREATE TABLE IF NOT EXISTS portfolio.asset
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticker TEXT NOT NULL,
            name TEXT NOT NULL,
            broker TEXT,
            currency TEXT,
            is_active BOOLEAN NOT NULL DEFAULT(True),
            from_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            to_timestamp TIMESTAMPTZ NOT NULL DEFAULT '9999-12-31'::timestamp,
            updated_timestamp TIMESTAMPTZ,
            CONSTRAINT unique_portfolio_asset_1
                UNIQUE (ticker, broker, currency)
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
               
    ALTER TABLE portfolio.industry
    DROP COLUMN is_active;

    ALTER TABLE portfolio.industry_history
    DROP COLUMN is_active;
    
    ALTER TABLE portfolio.sector
    DROP COLUMN is_active;

    ALTER TABLE portfolio.sector_history
    DROP COLUMN is_active;
    """)
