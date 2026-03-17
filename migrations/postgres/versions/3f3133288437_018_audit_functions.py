"""018_audit_functions

Revision ID: 3f3133288437
Revises: 3f8f7fe34497
Create Date: 2026-02-25 23:53:09.863546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f3133288437'
down_revision: Union[str, Sequence[str], None] = '3f8f7fe34497'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
               
        CREATE OR REPLACE FUNCTION portfolio.category_history()
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

        CREATE OR REPLACE TRIGGER category_versioning BEFORE DELETE OR UPDATE ON portfolio.category FOR EACH ROW EXECUTE FUNCTION portfolio.category_history();
        
        ALTER TABLE portfolio.tag
        ADD CONSTRAINT idx_portfolio_tag_name_category_unique UNIQUE(name, category_id);
        
    """)
    
    
    op.execute("""
               
                   
        CREATE OR REPLACE FUNCTION portfolio.sector_history()
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
                            industry_id,
                            name,
                            description,
                            created_timestamp,
                            updated_timestamp,
                            is_active
                        )
                        SELECT
                            ($1).id,
                            ($1).industry_id,
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

        CREATE OR REPLACE TRIGGER sector_versioning BEFORE DELETE OR UPDATE ON portfolio.sector FOR EACH ROW EXECUTE FUNCTION portfolio.sector_history();
                   
    """)

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
               
    CREATE OR REPLACE TRIGGER category_versioning BEFORE DELETE OR UPDATE ON portfolio.category FOR EACH ROW EXECUTE FUNCTION portfolio.record_history();
    
    DROP FUNCTION portfolio.category_history;
               
    CREATE OR REPLACE TRIGGER sector_versioning BEFORE DELETE OR UPDATE ON portfolio.sector FOR EACH ROW EXECUTE FUNCTION portfolio.record_history();
    
    DROP FUNCTION portfolio.sector_history;
    
    ALTER TABLE portfolio.tag
    DROP CONSTRAINT idx_portfolio_tag_name_category_unique;
               
    """)
