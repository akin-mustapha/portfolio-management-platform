"""002_portfolio_base_tables

Revision ID: 4400000000d2
Revises: 4400000000d1
Create Date: 2026-03-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4400000000d2"
down_revision: str | Sequence[str] | None = "4400000000d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "asset",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("external_id", sa.String, unique=True, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String),
        sa.Column("source_name", sa.String),
        sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="portfolio",
    )

    op.create_table(
        "category",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="portfolio",
    )

    op.create_table(
        "tag",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String, unique=True, nullable=False),
        sa.Column("description", sa.String),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("portfolio.category.id"),
        ),
        sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="portfolio",
    )

    op.create_table(
        "asset_tag",
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("portfolio.asset.id"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("portfolio.tag.id"),
            primary_key=True,
        ),
        sa.Column("is_active", sa.Boolean, server_default=sa.true(), nullable=False),
        sa.Column(
            "created_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True)),
        schema="portfolio",
    )

    op.create_table(
        "portfolio_snapshot",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("external_id", sa.String),
        sa.Column("data_timestamp", sa.DateTime(timezone=True)),
        sa.Column("currency", sa.String),
        sa.Column("current_value", sa.Float),
        sa.Column("total_value", sa.Float),
        sa.Column("total_cost", sa.Float),
        sa.Column("unrealized_profit", sa.Float),
        sa.Column("realized_profit", sa.Float),
        schema="portfolio",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("portfolio_snapshot", schema="portfolio")
    op.drop_table("asset_tag", schema="portfolio")
    op.drop_table("tag", schema="portfolio")
    op.drop_table("category", schema="portfolio")
    op.drop_table("asset", schema="portfolio")
