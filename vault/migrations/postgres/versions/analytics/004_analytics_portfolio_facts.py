"""004_analytics_portfolio_facts

Revision ID: 3300000000c4
Revises: 3300000000c3
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3300000000c4'
down_revision: Union[str, Sequence[str], None] = '3300000000c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "fact_valuation",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("unrealized_pnl", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics"
    )

    op.create_table(
        "fact_cashflow",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("cashflow", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics"
    )

    op.create_table(
        "fact_return",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_date.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset.asset_id"), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_portfolio.id"), nullable=False),
        sa.Column("sector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_sector.id"), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_tag.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics.dim_asset_type.id"), nullable=False),
        sa.Column("return", sa.Float, nullable=False),
        sa.Column("cumulative_return", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("fact_return", schema="analytics")
    op.drop_table("fact_cashflow", schema="analytics")
    op.drop_table("fact_valuation", schema="analytics")
