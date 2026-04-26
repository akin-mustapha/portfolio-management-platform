"""create raw_data table

Revision ID: b3bd31d8759b
Revises: 1ecedcc752f8
Create Date: 2026-01-10 22:18:21.167763

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3bd31d8759b"
down_revision: str | Sequence[str] | None = "1ecedcc752f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "raw_data",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("source", sa.String),
        sa.Column("payload", sa.String),
        sa.Column("is_processed", sa.Boolean, default=False),
        sa.Column("created_datetime", sa.DateTime, default=sa.func.now()),
        sa.Column("processed_datetime", sa.DateTime),
        # schema='stg'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("raw_data")
