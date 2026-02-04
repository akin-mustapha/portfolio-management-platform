"""create asset_data table

Revision ID: 1268104d5702
Revises: b3bd31d8759b
Create Date: 2026-01-15 22:49:47.347117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1268104d5702'
down_revision: Union[str, Sequence[str], None] = 'b3bd31d8759b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "asset_snapshot",
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('asset_id', sa.Integer, sa.ForeignKey('asset.id')),
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
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('asset_snapshot')

