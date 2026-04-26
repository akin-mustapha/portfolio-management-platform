"""005_raw_t212_history

Revision ID: 1100000000a5
Revises: 1100000000a4
Create Date: 2026-04-20

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1100000000a5"
down_revision: str | Sequence[str] | None = "1100000000a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS raw.t212_history_dividend (
            id                  TEXT NOT NULL,
            ingested_date       DATE NOT NULL,
            ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
            payload             JSONB NOT NULL,
            processed_at        TIMESTAMPTZ,
            PRIMARY KEY (id, ingested_date)
        )
        PARTITION BY RANGE (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_t212_history_dividend_ingested_date
        ON raw.t212_history_dividend (ingested_date);

        CREATE TABLE IF NOT EXISTS raw.t212_history_order (
            id                  TEXT NOT NULL,
            ingested_date       DATE NOT NULL,
            ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
            payload             JSONB NOT NULL,
            processed_at        TIMESTAMPTZ,
            PRIMARY KEY (id, ingested_date)
        )
        PARTITION BY RANGE (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_t212_history_order_ingested_date
        ON raw.t212_history_order (ingested_date);

        CREATE TABLE IF NOT EXISTS raw.t212_history_transaction (
            id                  TEXT NOT NULL,
            ingested_date       DATE NOT NULL,
            ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
            payload             JSONB NOT NULL,
            processed_at        TIMESTAMPTZ,
            PRIMARY KEY (id, ingested_date)
        )
        PARTITION BY RANGE (ingested_date);

        CREATE INDEX IF NOT EXISTS idx_raw_t212_history_transaction_ingested_date
        ON raw.t212_history_transaction (ingested_date);

        CREATE TABLE IF NOT EXISTS raw.t212_history_cursor (
            endpoint       TEXT PRIMARY KEY,
            last_cursor    TEXT,
            last_event_ts  TIMESTAMPTZ,
            updated_at     TIMESTAMPTZ DEFAULT now()
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP TABLE IF EXISTS raw.t212_history_cursor CASCADE;
        DROP TABLE IF EXISTS raw.t212_history_transaction CASCADE;
        DROP TABLE IF EXISTS raw.t212_history_order CASCADE;
        DROP TABLE IF EXISTS raw.t212_history_dividend CASCADE;
    """)
