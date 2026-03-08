"""019_add_sdc_silver

Revision ID: 1f0997560abd
Revises: 3f3133288437
Create Date: 2026-02-27 01:00:16.149293

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f0997560abd'
down_revision: Union[str, Sequence[str], None] = '3f3133288437'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE staging.industry
        CREATE TABLE staging.sector
        CREATE TABLE staging.tag
        CREATE TABLE staging.category
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TABLE staging.industry
        DROP TABLE staging.sector
        DROP TABLE staging.tag
        DROP TABLE staging.category
        """
    ) 
