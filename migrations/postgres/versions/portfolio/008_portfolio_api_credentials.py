"""008_portfolio_api_credentials

Revision ID: 4400000000d8
Revises: 4400000000d7
Create Date: 2026-03-21

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4400000000d8'
down_revision: Union[str, Sequence[str], None] = '4400000000d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE portfolio.api_credentials (
            id           SERIAL PRIMARY KEY,
            provider     VARCHAR(64) NOT NULL DEFAULT 'trading212',
            api_url      TEXT,
            api_key      TEXT NOT NULL,
            secret_token TEXT,
            updated_at   TIMESTAMP DEFAULT now(),
            CONSTRAINT uq_api_credentials_provider UNIQUE (provider)
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS portfolio.api_credentials;")
