"""005_portfolio_asset_v2

Revision ID: 4400000000d5
Revises: 4400000000d4
Create Date: 2026-03-18

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4400000000d5"
down_revision: str | Sequence[str] | None = "4400000000d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS portfolio.asset_v2
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticker TEXT NOT NULL,
            name TEXT NOT NULL,
            broker TEXT,
            currency TEXT,
            from_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            to_timestamp TIMESTAMPTZ NOT NULL DEFAULT '9999-12-31'::timestamp,
            updated_timestamp TIMESTAMPTZ,
            CONSTRAINT unique_portfolio_asset_1
                UNIQUE (ticker, broker, currency)
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS portfolio.asset_v2")
