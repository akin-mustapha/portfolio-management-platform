"""011_staging_rename_cashflow_cost_basis

Rename staging.asset_computed.cashflow → cost_basis.

The column was populated with `cost` (total invested capital), not a cash
movement delta. `cost_basis` is the correct name for that value.

Revision ID: 2200000000b11
Revises: 2200000000b10
Create Date: 2026-03-20

"""
from typing import Sequence, Union

from alembic import op


revision: str = '2200000000b11'
down_revision: Union[str, Sequence[str], None] = '2200000000b10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE staging.asset_computed RENAME COLUMN cashflow TO cost_basis")


def downgrade() -> None:
    op.execute("ALTER TABLE staging.asset_computed RENAME COLUMN cost_basis TO cashflow")
