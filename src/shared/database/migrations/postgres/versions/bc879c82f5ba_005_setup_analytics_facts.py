"""005_setup_analytics_facts

Revision ID: bc879c82f5ba
Revises: e49e07dbaa4b
Create Date: 2026-02-06 10:17:16.318308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'bc879c82f5ba'
down_revision: Union[str, Sequence[str], None] = 'e49e07dbaa4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # =========================
    # ASSET FACTS
    # =========================

    # Asset price (canonical market data)
    op.create_table(
        "fact_asset_price_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("average_price", sa.Float, nullable=False),
        sa.Column("opening_price", sa.Float, nullable=False),
        sa.Column("closing_price", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "asset_id",
            "date_id",
            name="uq_fact_asset_price_daily_grain"
        ),
        schema="analytics"
    )

    # Asset technical indicators
    op.create_table(
        "fact_asset_technical_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("pct_drawdown", sa.Float, nullable=False),
        sa.Column("ma_20d", sa.Float, nullable=False),
        sa.Column("ma_30d", sa.Float, nullable=False),
        sa.Column("ma_50d", sa.Float, nullable=False),
        sa.Column("volatility_20d", sa.Float, nullable=False),
        sa.Column("volatility_30d", sa.Float, nullable=False),
        sa.Column("volatility_50d", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "asset_id",
            "date_id",
            name="uq_fact_asset_technical_daily_grain"
        ),
        schema="analytics"
    )

    # Asset signals (opinions / strategy layer)
    op.create_table(
        "fact_asset_signal_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("dca_bias", sa.Float, nullable=False),
        sa.Column(
            "signal_version",
            sa.String,
            nullable=False,
            server_default="v1"
        ),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "asset_id",
            "date_id",
            "signal_version",
            name="uq_fact_asset_signal_daily_grain"
        ),
        schema="analytics"
    )

    # Asset returns
    op.create_table(
        "fact_asset_return_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("daily_return", sa.Float, nullable=False),
        sa.Column("cumulative_return", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "asset_id",
            "date_id",
            name="uq_fact_asset_return_daily_grain"
        ),
        schema="analytics"
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("fact_asset_price_daily", schema="analytics")
    op.drop_table("fact_asset_technical_daily", schema="analytics")
    op.drop_table("fact_asset_signal_daily", schema="analytics")
    op.drop_table("fact_asset_return_daily", schema="analytics")