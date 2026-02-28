"""016_update_silver_asset_computed-table-#53

Revision ID: 192a2efb33f5
Revises: c0a57dbfeb28
Create Date: 2026-02-21 15:45:07.439192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '192a2efb33f5'
down_revision: Union[str, Sequence[str], None] = 'c0a57dbfeb28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.execute("""
        DROP TABLE IF EXISTS staging.asset;
        CREATE TABLE staging.asset
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
            business_key TEXT NOT NULL UNIQUE,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp TIMESTAMPTZ
            
            
        )           
    """)
    
    
    
    op.execute("""
        DROP TABLE IF EXISTS staging.asset_computed;
        CREATE TABLE staging.asset_computed
        (
            asset_id UUID NOT NULL UNIQUE,
            cashflow FLOAT,
            daily_return FLOAT,
            cumulative_return FLOAT,
            dca_bias FLOAT,
            pct_drawdown FLOAT,
            recent_value_high_30d FLOAT,
            recent_value_low_30d FLOAT,
            recent_profit_high_30d FLOAT,
            recent_profit_low_30d FLOAT,
            value_high FLOAT,
            value_low FLOAT,
            ma_20d FLOAT,
            ma_30d FLOAT,
            ma_50d FLOAT,
            volatility_20d FLOAT,
            volatility_30d FLOAT,
            volatility_50d FLOAT,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT fk_asset_computed_asset_id
                FOREIGN KEY (asset_id)
                REFERENCES staging.asset(id)
            
            
        )           
    """)
    

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('asset_computed', schema="staging")
    op.drop_table('asset', schema="staging")
    op.execute("""
        CREATE TABLE staging.asset_v2
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
            business_key TEXT NOT NULL UNIQUE,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp TIMESTAMPTZ
            
            
        )           
    """)
    
    op.execute("""
        CREATE TABLE staging.asset_computed
        (
            asset_id UUID NOT NULL UNIQUE,
            cashflow FLOAT,
            daily_return FLOAT,
            cumulative_return FLOAT,
            dca_bias FLOAT,
            pct_drawdown FLOAT,
            recent_high_30d FLOAT,
            recent_low_30d FLOAT,
            high FLOAT,
            low FLOAT,
            ma_20d FLOAT,
            ma_30d FLOAT,
            ma_50d FLOAT,
            volatility_20d FLOAT,
            volatility_30d FLOAT,
            volatility_50d FLOAT,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT fk_asset_computed_asset_id
                FOREIGN KEY (asset_id)
                REFERENCES staging.asset_v2(id)
            
            
        )           
    """)
