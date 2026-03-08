"""010_create_scd_history_table

Revision ID: 1a61c607b4c0
Revises: c0002396119d
Create Date: 2026-02-09 21:18:04.637658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1a61c607b4c0'
down_revision: Union[str, Sequence[str], None] = 'c0002396119d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.execute(
        """            
            CREATE OR REPLACE FUNCTION portfolio.record_history()
            RETURNS trigger AS $$
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
                    'INSERT INTO %s SELECT ($1).*',
                    history_table
                )
                USING OLD;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            -- Create Audit Table
            CREATE TABLE portfolio.asset_history (LIKE portfolio.asset INCLUDING DEFAULTS INCLUDING GENERATED);
            
            ALTER TABLE portfolio.asset_history
            ADD COLUMN history_id UUID DEFAULT gen_random_uuid() PRIMARY KEY;

            CREATE TRIGGER asset_versioning
            BEFORE UPDATE OR DELETE
            ON portfolio.asset
            FOR EACH ROW
            EXECUTE FUNCTION portfolio.record_history();
        """
    )
    
    op.execute(
        """
            -- Create Audit Table
            CREATE TABLE portfolio.asset_tag_history (LIKE portfolio.asset_tag INCLUDING DEFAULTS INCLUDING GENERATED);
            
            ALTER TABLE portfolio.asset_tag_history
            ADD COLUMN history_id UUID DEFAULT gen_random_uuid() PRIMARY KEY;
            
            CREATE TRIGGER asset_tag_versioning
            BEFORE UPDATE OR DELETE
            ON portfolio.asset_tag
            FOR EACH ROW
            EXECUTE FUNCTION portfolio.record_history();
        """
    )
    
    op.execute(
        """
            -- Create Audit Table
            CREATE TABLE portfolio.tag_history (LIKE portfolio.tag INCLUDING DEFAULTS INCLUDING GENERATED);
            
            ALTER TABLE portfolio.tag_history
            ADD COLUMN history_id UUID DEFAULT gen_random_uuid() PRIMARY KEY;
            
            CREATE TRIGGER tag_versioning
            BEFORE UPDATE OR DELETE
            ON portfolio.tag
            FOR EACH ROW
            EXECUTE FUNCTION portfolio.record_history();
        """
    )
    
    op.execute(
        """
            -- Create Audit Table
            CREATE TABLE portfolio.category_history (LIKE portfolio.category INCLUDING DEFAULTS INCLUDING GENERATED);
            
            ALTER TABLE portfolio.category_history
            ADD COLUMN history_id UUID DEFAULT gen_random_uuid() PRIMARY KEY;
            
            CREATE TRIGGER category_versioning
            BEFORE UPDATE OR DELETE
            ON portfolio.category
            FOR EACH ROW
            EXECUTE FUNCTION portfolio.record_history();
        """
    )

def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS asset_versioning ON portfolio.asset;
        DROP TABLE IF EXISTS portfolio.asset_history;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS asset_tag_versioning ON portfolio.asset_tag;
        DROP TABLE IF EXISTS portfolio.asset_tag_history;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS tag_versioning ON portfolio.tag;
        DROP TABLE IF EXISTS portfolio.tag_history;
        """
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS category_versioning ON portfolio.category;
        DROP TABLE IF EXISTS portfolio.category_history;
        """
    )
    
    op.execute(
        """
        DROP FUNCTION IF EXISTS portfolio.record_history();
        """
    )
