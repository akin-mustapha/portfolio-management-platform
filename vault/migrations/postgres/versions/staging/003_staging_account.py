"""003_staging_account

Revision ID: 2200000000b3
Revises: 2200000000b2
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2200000000b3'
down_revision: Union[str, Sequence[str], None] = '2200000000b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE staging.account
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            data_timestamp TIMESTAMPTZ NOT NULL,
            external_id TEXT NOT NULL,
            cash_in_pies FLOAT,
            cash_available_to_trade FLOAT,
            cash_reserved_for_orders FLOAT,
            broker TEXT,
            currency TEXT,
            total_value FLOAT,
            investments_total_cost FLOAT,
            investments_realized_pnl FLOAT,
            investments_unrealized_pnl FLOAT,
            business_key TEXT NOT NULL UNIQUE,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp TIMESTAMPTZ
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS staging.account")
