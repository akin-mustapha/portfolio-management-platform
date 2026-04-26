"""010_portfolio_drop_rebalance_opaque_fields

Remove risk_tolerance and momentum_bias from portfolio.rebalance_config.
Neither field is read by generate_plan() — they were stored but had no effect.

Also widens the correction_days CHECK constraint from 1–7 to 1–30, matching
the updated slider range in the dashboard.

Revision ID: 4400000000da
Revises: 4400000000d9
Create Date: 2026-03-24

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4400000000da"
down_revision: str | Sequence[str] | None = "4400000000d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Drop unused columns and widen correction_days constraint."""
    op.execute("ALTER TABLE portfolio.rebalance_config DROP COLUMN IF EXISTS risk_tolerance;")
    op.execute("ALTER TABLE portfolio.rebalance_config DROP COLUMN IF EXISTS momentum_bias;")
    op.execute("""
        ALTER TABLE portfolio.rebalance_config
            DROP CONSTRAINT IF EXISTS rebalance_config_correction_days_check;
    """)
    op.execute("""
        ALTER TABLE portfolio.rebalance_config
            ADD CONSTRAINT rebalance_config_correction_days_check
                CHECK (correction_days BETWEEN 1 AND 30);
    """)


def downgrade() -> None:
    """Restore removed columns and original correction_days constraint."""
    op.execute("""
        ALTER TABLE portfolio.rebalance_config
            ADD COLUMN risk_tolerance SMALLINT NOT NULL DEFAULT 50
                CHECK (risk_tolerance BETWEEN 0 AND 100);
    """)
    op.execute("""
        ALTER TABLE portfolio.rebalance_config
            ADD COLUMN momentum_bias SMALLINT NOT NULL DEFAULT 0
                CHECK (momentum_bias BETWEEN -100 AND 100);
    """)
    op.execute("""
        ALTER TABLE portfolio.rebalance_config
            DROP CONSTRAINT IF EXISTS rebalance_config_correction_days_check;
    """)
    op.execute("""
        ALTER TABLE portfolio.rebalance_config
            ADD CONSTRAINT rebalance_config_correction_days_check
                CHECK (correction_days BETWEEN 1 AND 7);
    """)
