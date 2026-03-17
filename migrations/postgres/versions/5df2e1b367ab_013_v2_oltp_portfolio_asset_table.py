"""013_v2_oltp_portfolio_asset_table

Revision ID: 5df2e1b367ab
Revises: eee5d1e4f1c4
Create Date: 2026-02-13 20:40:16.077756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5df2e1b367ab'
down_revision: Union[str, Sequence[str], None] = 'eee5d1e4f1c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS portfolio.asset_v2
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticker TEXT NOT NULL,
            name TEXT NOT NULL,
            broker TEXT,
            currency TEXT,
            from_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            to_timestamp TIMESTAMPTZ NOT NULL DEFAULT '9999-12-31'::timestamp,
            updated_timestamp TIMESTAMPTZ,
            CONSTRAINT unique_portfolio_asset_1
                UNIQUE (ticker, broker, currency)
        );
    """)

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS portfolio.asset_v2")
