"""006_portfolio_restructure

Revision ID: 4400000000d6
Revises: 4400000000d5
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '4400000000d6'
down_revision: Union[str, Sequence[str], None] = '4400000000d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE portfolio.industry
        ADD COLUMN is_active Boolean DEFAULT (true);

        ALTER TABLE portfolio.industry_history
        ADD COLUMN is_active Boolean DEFAULT (true);


        ALTER TABLE portfolio.sector
        ADD COLUMN is_active Boolean DEFAULT(true);

        ALTER TABLE portfolio.sector_history
        ADD COLUMN is_active Boolean DEFAULT(true);

        DROP TABLE IF EXISTS portfolio.asset_tag;
        DROP TABLE IF EXISTS portfolio.asset;
        DROP TABLE IF EXISTS portfolio.asset_v2;
        CREATE TABLE IF NOT EXISTS portfolio.asset
        (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticker TEXT NOT NULL,
            name TEXT NOT NULL,
            broker TEXT,
            currency TEXT,
            is_active BOOLEAN NOT NULL DEFAULT(true),
            from_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            to_timestamp TIMESTAMPTZ NOT NULL DEFAULT '9999-12-31'::timestamp,
            updated_timestamp TIMESTAMPTZ,
            CONSTRAINT unique_portfolio_asset_1
                UNIQUE (ticker, broker, currency)
        );


        CREATE TABLE portfolio.asset_tag(
            asset_id uuid NOT NULL,
            tag_id uuid NOT NULL,
            is_active boolean NOT NULL DEFAULT true,
            created_timestamp timestamp with time zone NOT NULL DEFAULT now(),
            updated_timestamp timestamp with time zone,
            PRIMARY KEY(asset_id,tag_id),
            CONSTRAINT asset_tag_asset_id_fkey FOREIGN key(asset_id) REFERENCES portfolio.asset(id),
            CONSTRAINT asset_tag_tag_id_fkey FOREIGN key(tag_id) REFERENCES portfolio.tag(id)
        );


        CREATE OR REPLACE FUNCTION portfolio.industry_history()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
                    DECLARE
                        history_table text;
                    BEGIN
                        -- Convention: <table> → <table>_history
                        history_table := format(
                            '%I.%I_history',
                            TG_TABLE_SCHEMA,
                            TG_TABLE_NAME
                        );

                        EXECUTE format(
                            'INSERT INTO %s (
                            id,
                            name,
                            description,
                            created_timestamp,
                            updated_timestamp,
                            is_active
                        )
                        SELECT
                            ($1).id,
                            ($1).name,
                            ($1).description,
                            ($1).created_timestamp,
                            ($1).updated_timestamp,
                            ($1).is_active',
                            history_table
                        )
                        USING OLD;

                        RETURN NEW;
                    END;
                    $function$;

        CREATE OR REPLACE TRIGGER industry_versioning BEFORE DELETE OR UPDATE ON portfolio.industry FOR EACH ROW EXECUTE FUNCTION portfolio.industry_history();

        ALTER TABLE portfolio.category
        ADD COLUMN description varchar NULL;

        ALTER TABLE portfolio.category
        ADD COLUMN is_active boolean Default true;

        ALTER TABLE portfolio.category_history
        ADD COLUMN description varchar;

        ALTER TABLE portfolio.sector
        ADD CONSTRAINT unq_sector_name UNIQUE(name);

        ALTER TABLE portfolio.category_history
        ALTER COLUMN is_active DROP NOT NULL;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
    ALTER TABLE portfolio.industry
    DROP COLUMN is_active;

    ALTER TABLE portfolio.industry_history
    DROP COLUMN is_active;

    ALTER TABLE portfolio.sector
    DROP COLUMN is_active;

    ALTER TABLE portfolio.sector_history
    DROP COLUMN is_active;

    CREATE OR REPLACE TRIGGER industry_versioning BEFORE DELETE OR UPDATE ON portfolio.industry FOR EACH ROW EXECUTE FUNCTION portfolio.record_history();

    DROP FUNCTION portfolio.industry_history;

    ALTER TABLE portfolio.category
    DROP COLUMN description;

    ALTER TABLE portfolio.category
    DROP COLUMN is_active;

    ALTER TABLE portfolio.category_history
    DROP COLUMN description;

    ALTER TABLE portfolio.sector
    DROP CONSTRAINT unq_sector_name;
    """)
