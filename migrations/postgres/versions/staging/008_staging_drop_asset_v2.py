"""008_staging_drop_asset_v2

Revision ID: 2200000000b8
Revises: 2200000000b7
Create Date: 2026-03-19

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2200000000b8'
down_revision: Union[str, Sequence[str], None] = '2200000000b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop staging.asset_v2 — superseded by staging.asset in migration 004."""
    op.execute("DROP TABLE IF EXISTS staging.asset_v2")


def downgrade() -> None:
    """Restore staging.asset_v2."""
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
