"""012_create_silver_asset_computed_table

Revision ID: eee5d1e4f1c4
Revises: c9cb652df5fe
Create Date: 2026-02-10 19:23:29.760805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eee5d1e4f1c4'
down_revision: Union[str, Sequence[str], None] = 'c9cb652df5fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.execute("""
        CREATE TABLE portfolio.asset_v2
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            data_timestamp TIMESTAMPTZ NOT NULL,
            external_id TEXT,
            ticker TEXT,
            name TEXT NOT NULL,
            description TEXT,
            broker TEXT,
            currency TEXT,
            local_currency TEXT,
            share FLOAT,
            price FLOAT,
            avg_price FLOAT,
            value FLOAT,
            cost FLOAT,
            profit FLOAT,
            fx_impact FLOAT,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp TIMESTAMPTZ
            
            
        )           
    """)
    
    op.execute("""
        CREATE TABLE portfolio.asset_computed
        (
            asset_id UUID,
            cashflow FLOAT,
            return FLOAT,
            cumulative_return FLOAT,
            dca_bias FLOAT,
            pct_drawdown FLOAT,
            recent_high_30d FLOAT,
            recent_low_30d FLOAT,
            high FLOAT,
            low FLOAT,
            ma_20 FLOAT,
            ma_30 FLOAT,
            ma_50d FLOAT,
            volatility_20d FLOAT,
            volatility_30d FLOAT,
            volatility_50d FLOAT,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT fk_asset_computed_asset_id
                FOREIGN KEY (asset_id)
                REFERENCES portfolio.asset_v2(id)
            
            
        )           
    """)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('asset_computed', schema="portfolio")
    op.drop_table('asset_v2', schema="portfolio")