"""004_setup_analytics_dimensions

Revision ID: e49e07dbaa4b
Revises: 45194c0958fb
Create Date: 2026-02-06 10:06:45.135467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e49e07dbaa4b'
down_revision: Union[str, Sequence[str], None] = '45194c0958fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "dim_date",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date", sa.Date, nullable=False, unique=True),
        sa.Column("year", sa.Integer, nullable=False, unique=False),
        sa.Column("month", sa.Integer, nullable=False, unique=False),
        sa.Column("day_of_week", sa.Integer, nullable=False, unique=False),
        sa.Column("quarter", sa.Integer, nullable=False, unique=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),
        schema="analytics"
    )
    op.create_table(
        "dim_time",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("time", sa.Time, nullable=False, unique=True),
        sa.Column("hour", sa.Integer, nullable=False, unique=False),
        sa.Column("minute", sa.Integer, nullable=False, unique=False),
        sa.Column("second", sa.Integer, nullable=False, unique=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),
        schema="analytics"
    )
    op.create_table(
        "dim_asset",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("ticker", sa.String, nullable=False, unique=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("asset_type", sa.String, nullable=False),
        sa.Column("exchange", sa.String, nullable=True, unique=False),
        sa.Column("currency", sa.String, nullable=True, unique=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("asset_id", name="uq_dim_asset_asset_id"),
        schema="analytics"
    )
    op.create_table(
        "dim_portfolio",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("portfolio_id", sa.String, nullable=False, unique=True),
        sa.Column("name", sa.String, nullable=False, unique=True),
        sa.Column("base_currency", sa.String, nullable=False),
        sa.Column(
            "created_datetime",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),
        schema="analytics"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("dim_date", schema="analytics")
    op.drop_table("dim_time", schema="analytics")
    op.drop_table("dim_asset", schema="analytics")
    op.drop_table("dim_portfolio", schema="analytics")