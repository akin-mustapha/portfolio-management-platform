"""014_portfolio_asset_sector_industry

Adds sector_id and industry_id FK columns to portfolio.asset and populates
classifications for all individual stocks.

ETFs, ETCs, and index funds are left NULL — they span multiple sectors.

Revision ID: 4400000000de
Revises: 4400000000dd
Create Date: 2026-04-25
"""
from typing import Sequence, Union

from alembic import op

revision: str = "4400000000de"
down_revision: Union[str, None] = "4400000000dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (ticker, sector.id, industry.id) — UUIDs from portfolio.sector / portfolio.industry
# sector.id     → portfolio.sector.id  (PK, unique)
# industry.id   → portfolio.industry.id (PK, unique)
_CLASSIFICATIONS = [
    # Technology / Hardware
    ("AAPL",   "ca24df5e-e5c8-4fec-9599-30f874dd73d1", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("SMCI",   "ca24df5e-e5c8-4fec-9599-30f874dd73d1", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    # Technology / Software
    ("MSFT",   "77941094-60d6-4d99-bb9d-b80f9b9847e9", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("ADBE",   "77941094-60d6-4d99-bb9d-b80f9b9847e9", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("PLTR",   "77941094-60d6-4d99-bb9d-b80f9b9847e9", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("SNII",   "77941094-60d6-4d99-bb9d-b80f9b9847e9", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    # Technology / Semiconductors
    ("NVDd",   "f06bc951-e640-4165-9c22-061035c1f456", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("AMDd",   "f06bc951-e640-4165-9c22-061035c1f456", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("ASMLa",  "f06bc951-e640-4165-9c22-061035c1f456", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    ("TSM",    "f06bc951-e640-4165-9c22-061035c1f456", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    # Technology / IT Services
    ("AMZN",   "aeba4050-064e-4f6d-b1a8-6bf53b8c8187", "380dcb63-79ff-4add-bbd8-513a7a4f0a83"),
    # Communication Services / Internet & Media
    ("GOOGL",  "6981f0de-0b0d-43b3-b326-5359df7cd93c", "249142d8-8900-475f-9b57-f15fd4640a3f"),
    ("FB",     "6981f0de-0b0d-43b3-b326-5359df7cd93c", "249142d8-8900-475f-9b57-f15fd4640a3f"),
    # Communication Services / Media & Entertainment
    ("EA",     "6725bde5-3dba-4c09-8713-6b3cf39edb62", "249142d8-8900-475f-9b57-f15fd4640a3f"),
    ("SNE",    "6725bde5-3dba-4c09-8713-6b3cf39edb62", "249142d8-8900-475f-9b57-f15fd4640a3f"),
    # Consumer Discretionary / Automotive
    ("TSLA",   "b7e27cf1-81fc-401a-8544-c8c00c18ff96", "3305e7e2-4fa6-45bd-b362-3366df9be7f8"),
    # Consumer Discretionary / Retail
    ("NKE",    "03b43466-baf9-463c-a28d-6c8537f4ef7e", "3305e7e2-4fa6-45bd-b362-3366df9be7f8"),
    # Consumer Staples / Food & Beverages
    ("KO",     "19ba0016-21b7-42bb-8184-99c06422a091", "dab50a95-885c-4736-b06b-f02bc1e95e18"),
    # Consumer Staples / Household Products
    ("BMT1d",  "de88e860-16eb-4ced-8f62-874a94a90162", "dab50a95-885c-4736-b06b-f02bc1e95e18"),
    # Healthcare / Pharmaceuticals
    ("PFE",    "2f35a427-7995-4e84-9f7c-9a0f8d1fb945", "0e24e223-7784-41c9-88a4-48b945660114"),
    # Healthcare / Healthcare Services
    ("UNH",    "7a8561f7-230d-45fe-982c-638e6ebd4d15", "0e24e223-7784-41c9-88a4-48b945660114"),
    # Financials / Insurance
    ("ALVd",   "7818efd6-fb3d-40ea-a5d0-48386c6ad9e6", "2acea78b-ccb4-40ed-98cf-860d35741660"),
    ("SFGYY",  "7818efd6-fb3d-40ea-a5d0-48386c6ad9e6", "2acea78b-ccb4-40ed-98cf-860d35741660"),
    # Energy / Oil & Gas
    ("CHVd",   "2b80a561-c81a-414a-a3a7-c04a063fb672", "f180fc82-968e-42f3-8c97-6fb9a4431c5d"),
    ("SHELl",  "2b80a561-c81a-414a-a3a7-c04a063fb672", "f180fc82-968e-42f3-8c97-6fb9a4431c5d"),
    # Industrials / Aerospace & Defence
    ("AIRp",   "05de02aa-72a7-4c25-8cc5-995b9990a974", "79767d45-a23b-4085-b1d1-1dacbd79cd8a"),
]


def upgrade() -> None:
    op.execute("""
        ALTER TABLE portfolio.asset
            ADD COLUMN IF NOT EXISTS sector_id   uuid REFERENCES portfolio.sector(id),
            ADD COLUMN IF NOT EXISTS industry_id uuid REFERENCES portfolio.industry(id)
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_portfolio_asset_sector_id   ON portfolio.asset (sector_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_portfolio_asset_industry_id ON portfolio.asset (industry_id)")

    for ticker, sector_id, industry_id in _CLASSIFICATIONS:
        op.execute(f"""
            UPDATE portfolio.asset
            SET sector_id   = '{sector_id}',
                industry_id = '{industry_id}'
            WHERE ticker = '{ticker}'
        """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS portfolio.ix_portfolio_asset_industry_id")
    op.execute("DROP INDEX IF EXISTS portfolio.ix_portfolio_asset_sector_id")
    op.execute("""
        ALTER TABLE portfolio.asset
            DROP COLUMN IF EXISTS industry_id,
            DROP COLUMN IF EXISTS sector_id
    """)
