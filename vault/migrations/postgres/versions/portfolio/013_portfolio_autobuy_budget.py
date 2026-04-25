"""013_portfolio_autobuy_budget

Adds portfolio.autobuy_budget to persist monthly spend for the autobuy script,
replacing the state.json file.

Revision ID: 4400000000dd
Revises: 4400000000dc
Create Date: 2026-04-24
"""
from typing import Sequence, Union

from alembic import op


revision: str = "4400000000dd"
down_revision: Union[str, Sequence[str], None] = "4400000000dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS portfolio.autobuy_budget (
            month        CHAR(7)       NOT NULL,
            spent        NUMERIC(12,2) NOT NULL DEFAULT 0,
            updated_at   TIMESTAMPTZ   NOT NULL DEFAULT now(),
            CONSTRAINT pk_autobuy_budget PRIMARY KEY (month)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS portfolio.autobuy_budget CASCADE")
