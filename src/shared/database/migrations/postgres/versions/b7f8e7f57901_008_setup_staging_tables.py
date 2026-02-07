"""008_setup_staging_tables

Revision ID: b7f8e7f57901
Revises: ec8b1de1afc0
Create Date: 2026-02-07 20:05:43.856890

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b7f8e7f57901'
down_revision: Union[str, Sequence[str], None] = 'ec8b1de1afc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Portfolio positions (ownership truth)
    op.create_table(
        "asset",
        sa.Column('ticker', sa.String, unique=False, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('source_name', sa.String),
        sa.Column('currency', sa.String),
        sa.Column('quantity', sa.Float),
        sa.Column('quantity_available_for_trading', sa.Float),
        sa.Column('quantity_in_pies', sa.Float),
        sa.Column('current_price', sa.Float),
        sa.Column('average_price_paid', sa.Float),
        sa.Column('total_cost', sa.Float),
        sa.Column('current_value', sa.Float),
        sa.Column('unrealized_profit_loss', sa.Float),
        sa.Column('fx_impact', sa.Float),
        sa.Column('created_timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        schema="staging"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('asset', schema='staging')
