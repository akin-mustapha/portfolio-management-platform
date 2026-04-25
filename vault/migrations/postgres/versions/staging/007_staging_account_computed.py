"""007_staging_account_computed

Revision ID: 2200000000b7
Revises: 2200000000b6
Create Date: 2026-03-19

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2200000000b7'
down_revision: Union[str, Sequence[str], None] = '2200000000b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE staging.account_computed
        (
            account_id UUID NOT NULL,
            total_return_abs FLOAT,
            total_return_pct FLOAT,
            cash_deployment_ratio FLOAT,
            daily_change_abs FLOAT,
            daily_change_pct FLOAT,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT uq_account_computed_account_id UNIQUE (account_id),

            CONSTRAINT fk_account_computed_account_id
                FOREIGN KEY (account_id)
                REFERENCES staging.account(id)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS staging.account_computed")
