"""011_portfolio_seed_reference_data

Revision ID: 4400000000dc
Revises: 4400000000db
Create Date: 2026-04-22

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4400000000dc'
down_revision: Union[str, Sequence[str], None] = '4400000000db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  pass
    # op.execute("""
    #     ALTER TABLE "asset" ADD COLUMN "auto_trading" BOOLEAN DEFAULT false ;
    # """)



def downgrade() -> None:
  pass
    # op.execute("""
    #     ALTER TABLE "asset" DROP COLUMN "auto_trading";
    # """)
