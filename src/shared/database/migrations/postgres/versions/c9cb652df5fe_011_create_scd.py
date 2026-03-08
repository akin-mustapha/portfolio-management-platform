"""011_create_scd

Revision ID: c9cb652df5fe
Revises: 1a61c607b4c0
Create Date: 2026-02-09 21:55:30.926415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9cb652df5fe'
down_revision: Union[str, Sequence[str], None] = '1a61c607b4c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        -- =========================
        -- Industry table
        -- =========================
        CREATE TABLE IF NOT EXISTS portfolio.industry (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp TIMESTAMPTZ
        );

        -- Industry history
        CREATE TABLE IF NOT EXISTS portfolio.industry_history
        (LIKE portfolio.industry INCLUDING DEFAULTS INCLUDING GENERATED);
        
        ALTER TABLE portfolio.industry_history
        ADD COLUMN history_id UUID DEFAULT gen_random_uuid() PRIMARY KEY;

        CREATE TRIGGER industry_versioning
        BEFORE UPDATE OR DELETE
        ON portfolio.industry
        FOR EACH ROW
        EXECUTE FUNCTION portfolio.record_history();


        -- =========================
        -- Sector table
        -- =========================
        CREATE TABLE IF NOT EXISTS portfolio.sector (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            industry_id UUID NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_timestamp TIMESTAMPTZ,

            CONSTRAINT fk_sector_industry
                FOREIGN KEY (industry_id)
                REFERENCES portfolio.industry(id)
        );

        -- Sector history
        CREATE TABLE IF NOT EXISTS portfolio.sector_history
        (LIKE portfolio.sector INCLUDING DEFAULTS INCLUDING GENERATED);
        
        
        ALTER TABLE portfolio.sector_history
        ADD COLUMN history_id UUID DEFAULT gen_random_uuid() PRIMARY KEY;

        CREATE TRIGGER sector_versioning
        BEFORE UPDATE OR DELETE
        ON portfolio.sector
        FOR EACH ROW
        EXECUTE FUNCTION portfolio.record_history();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS sector_versioning ON portfolio.sector;
        DROP TABLE IF EXISTS portfolio.sector_history;
        DROP TABLE IF EXISTS portfolio.sector;

        DROP TRIGGER IF EXISTS industry_versioning ON portfolio.industry;
        DROP TABLE IF EXISTS portfolio.industry_history;
        DROP TABLE IF EXISTS portfolio.industry;
        """
    )