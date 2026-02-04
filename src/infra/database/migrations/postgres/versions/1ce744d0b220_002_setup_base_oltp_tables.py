"""002_setup_base_OLTP_tables

Revision ID: 1ce744d0b220
Revises: 941ca72a5bf5
Create Date: 2026-02-04 18:14:23.679537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ce744d0b220'
down_revision: Union[str, Sequence[str], None] = '941ca72a5bf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "asset",
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('external_id', sa.String, unique=True),
        sa.Column('name', sa.String),
        sa.Column('description', sa.String),
        sa.Column('source_name', sa.String),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_timestamp', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_timestamp', sa.DateTime),

        schema='portfolio'
    )
    op.create_table(
        "tag_category",
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('name', sa.String, unique=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_timestamp', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_timestamp', sa.DateTime),

        schema='portfolio'
    )
    op.create_table(
        "tag",
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('name', sa.String, unique=True),
        sa.Column('description', sa.String),
        sa.Column('tag_category_id', sa.UUID, sa.ForeignKey('portfolio.tag_category.id')),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_timestamp', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_timestamp', sa.DateTime),
        schema='portfolio'
    )


    op.create_table(
        "asset_tag",
        sa.Column('asset_id', sa.UUID, sa.ForeignKey('portfolio.asset.id'), primary_key=True),
        sa.Column('tag_id', sa.UUID, sa.ForeignKey('portfolio.tag.id'), primary_key=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_timestamp', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_timestamp', sa.DateTime),

        schema='portfolio'
    )
    op.create_table(
        "asset_snapshot",
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('asset_id', sa.UUID, sa.ForeignKey('portfolio.asset.id')),
        sa.Column('data_date', sa.DateTime),
        sa.Column('currency', sa.String),
        sa.Column('local_currency', sa.String),
        sa.Column('share', sa.Float),
        sa.Column('price', sa.Float),
        sa.Column('avg_price', sa.Float),
        sa.Column('value', sa.Float),
        sa.Column('cost', sa.Float),
        sa.Column('profit', sa.Float),
        sa.Column('fx_impact', sa.Float),
        schema='portfolio'
    )
    op.create_table(
        "asset_metric",
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('asset_id', sa.UUID, sa.ForeignKey('portfolio.asset.id')),
        sa.Column('data_date', sa.DateTime),
        sa.Column('pct_drawdown', sa.Float),
        sa.Column('recent_high_30d', sa.Float),
        sa.Column('recent_low_30d', sa.Float),
        sa.Column('ma_30', sa.Float),
        sa.Column('norm_price_30d', sa.Float),
        sa.Column('volatility_30d', sa.Float),
        sa.Column('price_vs_ma_50', sa.Float),
        sa.Column('ma_50', sa.Float),
        sa.Column('dca_bias', sa.Float),

        schema='portfolio'
    )
    op.create_table(
        "portfolio_snapshot",
        sa.Column('id', sa.UUID, primary_key=True),
        sa.Column('external_id', sa.String),
        sa.Column('data_date', sa.DateTime),
        sa.Column('currency', sa.String),
        sa.Column('current_value', sa.Float),
        sa.Column('total_value', sa.Float),
        sa.Column('total_cost', sa.Float),
        sa.Column('unrealized_profit', sa.Float),
        sa.Column('realized_profit', sa.Float),

        schema='portfolio'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('asset_tag', schema='portfolio')
    op.drop_table('tag_category', schema='portfolio')
    op.drop_table('tag', schema='portfolio')
    op.drop_table('asset', schema='portfolio')
    op.drop_table('asset_snapshot', schema='portfolio')
    op.drop_table('portfolio_snapshot', schema='portfolio')

