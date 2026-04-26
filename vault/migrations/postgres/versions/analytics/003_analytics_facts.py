"""003_analytics_facts

Revision ID: 3300000000c3
Revises: 3300000000c2
Create Date: 2026-03-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3300000000c3"
down_revision: str | Sequence[str] | None = "3300000000c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "fact_price",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False,
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False,
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False,
        ),
        sa.Column(
            "sector_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_sector.id"),
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_tag.id"),
            nullable=False,
        ),
        sa.Column(
            "asset_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset_type.id"),
            nullable=False,
        ),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("average_price", sa.Float, nullable=False),
        sa.Column("open_price", sa.Float, nullable=False),
        sa.Column("close_price", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )

    op.create_table(
        "fact_technical",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False,
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False,
        ),
        sa.Column(
            "sector_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_sector.id"),
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_tag.id"),
            nullable=False,
        ),
        sa.Column(
            "asset_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset_type.id"),
            nullable=False,
        ),
        sa.Column("pct_drawdown", sa.Float, nullable=False),
        sa.Column("ma_20d", sa.Float, nullable=False),
        sa.Column("ma_30d", sa.Float, nullable=False),
        sa.Column("ma_50d", sa.Float, nullable=False),
        sa.Column("volatility_20d", sa.Float, nullable=False),
        sa.Column("volatility_30d", sa.Float, nullable=False),
        sa.Column("volatility_50d", sa.Float, nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )

    op.create_table(
        "fact_signal",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.asset_id"),
            nullable=False,
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False,
        ),
        sa.Column(
            "sector_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_sector.id"),
            nullable=False,
        ),
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_tag.id"),
            nullable=False,
        ),
        sa.Column(
            "asset_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset_type.id"),
            nullable=False,
        ),
        sa.Column("dca_bias", sa.Float, nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="analytics",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("fact_signal", schema="analytics")
    op.drop_table("fact_technical", schema="analytics")
    op.drop_table("fact_price", schema="analytics")
