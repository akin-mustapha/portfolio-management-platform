"""002_staging_asset_tables

Revision ID: 2200000000b2
Revises: 2200000000b1
Create Date: 2026-03-18

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2200000000b2"
down_revision: str | Sequence[str] | None = "2200000000b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
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


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS staging.asset_computed")
    op.execute("DROP TABLE IF EXISTS staging.asset_v2")
