"""005_analytics_populate_dates

Revision ID: 3300000000c5
Revises: 3300000000c4
Create Date: 2026-03-18

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3300000000c5"
down_revision: str | Sequence[str] | None = "3300000000c4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    INSERT INTO analytics.dim_date (
        date,
        year,
        quarter,
        month,
        month_name,
        day_of_month,
        day_of_week,
        day_name,
        is_weekend,
        is_month_start,
        is_month_end,
        is_year_start,
        is_year_end
    )
    SELECT
        d::date                                         AS date,
        EXTRACT(YEAR FROM d)::int                       AS year,
        EXTRACT(QUARTER FROM d)::int                    AS quarter,
        EXTRACT(MONTH FROM d)::int                      AS month,
        TO_CHAR(d, 'Month')                             AS month_name,
        EXTRACT(DAY FROM d)::int                        AS day_of_month,
        EXTRACT(DOW FROM d)::int                        AS day_of_week,
        TO_CHAR(d, 'Day')                               AS day_name,
        EXTRACT(DOW FROM d) IN (0, 6)                   AS is_weekend,
        d = date_trunc('month', d)::date                AS is_month_start,
        d = (date_trunc('month', d)
            + interval '1 month - 1 day')::date        AS is_month_end,
        d = date_trunc('year', d)::date                 AS is_year_start,
        d = (date_trunc('year', d)
            + interval '1 year - 1 day')::date         AS is_year_end
    FROM generate_series(
        '2000-01-01'::date,
        '2035-12-31'::date,
        interval '1 day'
    ) AS d;
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
