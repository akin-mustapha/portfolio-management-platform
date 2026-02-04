"""003_setup_base_staging_tables

Revision ID: 45194c0958fb
Revises: 1ce744d0b220
Create Date: 2026-02-04 18:30:15.774483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '45194c0958fb'
down_revision: Union[str, Sequence[str], None] = '1ce744d0b220'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "raw_data",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source", sa.String, nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("is_processed", sa.Boolean, server_default=sa.false(), nullable=False),
        sa.Column("created_datetime", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("processed_datetime", sa.DateTime(timezone=True)),
        schema="staging"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('raw_data', schema='staging')