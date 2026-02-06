"""006_setup_analytics_portfolio_facts

Revision ID: c0f773873a1d
Revises: bc879c82f5ba
Create Date: 2026-02-06 11:23:42.920292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c0f773873a1d'
down_revision: Union[str, Sequence[str], None] = 'bc879c82f5ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # =========================
    # PORTFOLIO FACTS
    # =========================

    # Portfolio positions (ownership truth)
    op.create_table(
        "fact_portfolio_position_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_asset.id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("quantity", sa.Float, nullable=False),
        sa.Column("cost_basis", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "portfolio_id",
            "asset_id",
            "date_id",
            name="uq_fact_portfolio_position_daily_grain"
        ),
        schema="analytics"
    )

    # Portfolio valuation
    op.create_table(
        "fact_portfolio_valuation_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("market_value", sa.Float, nullable=False),
        sa.Column("unrealized_pnl", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "portfolio_id",
            "date_id",
            name="uq_fact_portfolio_valuation_daily_grain"
        ),
        schema="analytics"
    )

    # Portfolio cash flows
    op.create_table(
        "fact_portfolio_cashflow_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("cash_flow", sa.Float, nullable=False),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "portfolio_id",
            "date_id",
            name="uq_fact_portfolio_cashflow_daily_grain"
        ),
        schema="analytics"
    )

    # Portfolio performance
    op.create_table(
        "fact_portfolio_return_daily",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "portfolio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_portfolio.id"),
            nullable=False
        ),
        sa.Column(
            "date_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analytics.dim_date.id"),
            nullable=False
        ),
        sa.Column("daily_return", sa.Float, nullable=False),
        sa.Column("twr", sa.Float, nullable=True),
        sa.Column("mwr", sa.Float, nullable=True),
        sa.Column("created_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_timestamp", sa.DateTime(timezone=True), nullable=False),

        sa.UniqueConstraint(
            "portfolio_id",
            "date_id",
            name="uq_fact_portfolio_return_daily_grain"
        ),
        schema="analytics"
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("fact_portfolio_valuation_daily", schema="analytics")
    op.drop_table("fact_portfolio_cashflow_daily", schema="analytics")
    op.drop_table("fact_portfolio_return_daily", schema="analytics")
    op.drop_table("fact_portfolio_position_daily", schema="analytics")