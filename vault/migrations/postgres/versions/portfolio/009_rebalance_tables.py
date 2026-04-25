"""009_rebalance_tables

Revision ID: 4400000000d9
Revises: 4400000000d8
Create Date: 2026-03-23

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4400000000d9'
down_revision: Union[str, Sequence[str], None] = '4400000000d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE portfolio.rebalance_config (
            id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            asset_id                UUID NOT NULL REFERENCES portfolio.asset(id),
            target_weight_pct       NUMERIC(5,2) NOT NULL,
            min_weight_pct          NUMERIC(5,2) NOT NULL DEFAULT 0.0,
            max_weight_pct          NUMERIC(5,2) NOT NULL DEFAULT 100.0,
            risk_tolerance          SMALLINT NOT NULL DEFAULT 50
                                        CHECK (risk_tolerance BETWEEN 0 AND 100),
            rebalance_threshold_pct NUMERIC(5,2) NOT NULL DEFAULT 2.0,
            correction_days         SMALLINT NOT NULL DEFAULT 3
                                        CHECK (correction_days BETWEEN 1 AND 7),
            momentum_bias           SMALLINT NOT NULL DEFAULT 0
                                        CHECK (momentum_bias BETWEEN -100 AND 100),
            is_active               BOOLEAN NOT NULL DEFAULT TRUE,
            created_timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT uq_rebalance_config_asset UNIQUE (asset_id)
        );
    """)

    op.execute("""
        CREATE TABLE portfolio.rebalance_plan (
            id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_date           DATE NOT NULL DEFAULT CURRENT_DATE,
            target_completion_date DATE NOT NULL,
            status                 VARCHAR(20) NOT NULL DEFAULT 'draft'
                                       CHECK (status IN ('draft','active','completed','cancelled')),
            plan_json              JSONB NOT NULL DEFAULT '{}',
            email_sent             BOOLEAN NOT NULL DEFAULT FALSE,
            created_timestamp      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp      TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS portfolio.rebalance_plan;")
    op.execute("DROP TABLE IF EXISTS portfolio.rebalance_config;")
