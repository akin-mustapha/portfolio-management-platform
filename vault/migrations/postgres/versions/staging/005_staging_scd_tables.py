"""005_staging_scd_tables

Revision ID: 2200000000b5
Revises: 2200000000b4
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '2200000000b5'
down_revision: Union[str, Sequence[str], None] = '2200000000b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
            CREATE TABLE staging.industry(
                id uuid NOT NULL DEFAULT gen_random_uuid(),
                industry_id uuid NOT NULL,
                name text NOT NULL,
                description text NOT NULL,
                is_current boolean DEFAULT true,
                from_timestamp timestamp with time zone NOT NULL DEFAULT now(),
                to_timestamp timestamp with time zone,
                PRIMARY KEY(id, from_timestamp)
            );

            CREATE TABLE staging.sector(
                id uuid NOT NULL DEFAULT gen_random_uuid(),
                sector_id uuid NOT NULL,
                industry_id uuid NOT NULL,
                name text NOT NULL,
                description text,
                is_current boolean DEFAULT true,
                from_timestamp timestamp with time zone NOT NULL DEFAULT now(),
                to_timestamp timestamp with time zone,
                PRIMARY KEY(id, from_timestamp)
            );

            CREATE TABLE staging.tag(
                id uuid NOT NULL DEFAULT gen_random_uuid(),
                tag_id uuid NOT NULL,
                name varchar NOT NULL,
                description varchar,
                category_id uuid,
                is_current boolean NOT NULL DEFAULT true,
                from_timestamp timestamp with time zone NOT NULL DEFAULT now(),
                to_timestamp timestamp with time zone,
                PRIMARY KEY(id, from_timestamp)
            );

            CREATE TABLE staging.category(
                id uuid NOT NULL DEFAULT gen_random_uuid(),
                category_id uuid NOT NULL,
                name varchar NOT NULL,
                description varchar,
                is_current boolean DEFAULT true,
                from_timestamp timestamp with time zone NOT NULL DEFAULT now(),
                to_timestamp timestamp with time zone,
                PRIMARY KEY(id, from_timestamp)
            );

            CREATE TABLE staging.asset_tag(
                id uuid NOT NULL DEFAULT gen_random_uuid(),
                asset_id uuid NOT NULL,
                tag_id uuid NOT NULL,
                is_current boolean DEFAULT true,
                from_timestamp timestamp with time zone NOT NULL DEFAULT now(),
                to_timestamp timestamp with time zone,
                PRIMARY KEY(id, from_timestamp)
            );
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TABLE staging.industry;
        DROP TABLE staging.sector;
        DROP TABLE staging.tag;
        DROP TABLE staging.category;
        DROP TABLE staging.asset_tag;
        """
    )
