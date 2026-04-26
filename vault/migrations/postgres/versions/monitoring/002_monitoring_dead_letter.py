"""002_monitoring_dead_letter

Revision ID: 5500000000e2
Revises: 5500000000e1
Create Date: 2026-03-20

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5500000000e2"
down_revision: str | Sequence[str] | None = "5500000000e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE monitoring.dead_letter (
            id              BIGSERIAL PRIMARY KEY,
            pipeline_name   TEXT NOT NULL,
            layer           TEXT NOT NULL,
            business_key    TEXT,
            raw_payload     JSONB NOT NULL,
            error_type      TEXT NOT NULL,
            error_message   TEXT NOT NULL,
            rejected_at     TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE INDEX idx_dead_letter_pipeline_name
        ON monitoring.dead_letter (pipeline_name)
    """)

    op.execute("""
        CREATE INDEX idx_dead_letter_rejected_at
        ON monitoring.dead_letter (rejected_at)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS monitoring.dead_letter")
