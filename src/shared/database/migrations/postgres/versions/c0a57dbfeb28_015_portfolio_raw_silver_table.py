"""015_portfolio_raw_silver_table

Revision ID: c0a57dbfeb28
Revises: 4ce1cda63acb
Create Date: 2026-02-16 00:40:12.346867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0a57dbfeb28'
down_revision: Union[str, Sequence[str], None] = '4ce1cda63acb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.execute("""
        CREATE TABLE staging.portfolio
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            data_timestamp TIMESTAMPTZ NOT NULL,
            external_id TEXT NOT NULL,
            cash_in_pies FLOAT,
            cash_available_to_trade FLOAt,
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
    op.execute("DROP TABLE IF EXISTS staging.portfolio")