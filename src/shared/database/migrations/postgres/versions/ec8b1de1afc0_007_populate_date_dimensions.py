"""007_populate_date_dimensions

Revision ID: ec8b1de1afc0
Revises: c0f773873a1d
Create Date: 2026-02-06 15:57:50.797413

"""
from calendar import month
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec8b1de1afc0'
down_revision: Union[str, Sequence[str], None] = 'c0f773873a1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO analytics.dim_date (date, year, month, day_of_week, quarter)
        SELECT
            date,
            EXTRACT(YEAR FROM date) as year,
            EXTRACT(MONTH FROM date) as month,
            EXTRACT(DOW FROM date) as day_of_week,
            EXTRACT(QUARTER FROM date) as quarter
        FROM generate_series(
            '2000-01-01'::date,
            '2035-12-31'::date,
            interval '1 day'
        ) as date
    """)

    op.execute("""
        INSERT INTO analytics.dim_time (time, hour, minute, second)
            SELECT
                gs::time AS time,
                EXTRACT(HOUR FROM gs)   AS hour,
                EXTRACT(MINUTE FROM gs) AS minute,
                EXTRACT(SECOND FROM gs) AS second
            FROM generate_series(
                '2000-01-01 00:00:00'::timestamp,
                '2000-01-01 23:59:00'::timestamp,
                interval '1 minute'
            ) AS gs;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM analytics.dim_date")
    op.execute("DELETE FROM analytics.dim_time")
