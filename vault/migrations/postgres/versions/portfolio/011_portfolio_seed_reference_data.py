"""011_portfolio_seed_reference_data

Revision ID: 4400000000db
Revises: 4400000000da
Create Date: 2026-04-07

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4400000000db"
down_revision: str | Sequence[str] | None = "4400000000da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Categories (UNIQUE on name — safe to use ON CONFLICT)
    op.execute("""
        INSERT INTO portfolio.category (name, is_active)
        VALUES
            ('Asset Type', true),
            ('Geography',  true),
            ('Strategy',   true),
            ('Theme',      true)
        ON CONFLICT (name) DO NOTHING;
    """)

    # 2. Industries (UNIQUE on name — safe to use ON CONFLICT)
    op.execute("""
        INSERT INTO portfolio.industry (name, description)
        VALUES
            ('Technology',             'Software, hardware, and semiconductors'),
            ('Healthcare',             'Pharmaceuticals, biotech, and medical devices'),
            ('Financials',             'Banks, insurance, and asset management'),
            ('Consumer Discretionary', 'Retail, automotive, and leisure'),
            ('Consumer Staples',       'Food, beverages, and household products'),
            ('Energy',                 'Oil, gas, and renewable energy'),
            ('Industrials',            'Aerospace, defence, and manufacturing'),
            ('Materials',              'Chemicals, metals, and mining'),
            ('Real Estate',            'REITs and real estate services'),
            ('Utilities',              'Electric, gas, and water utilities'),
            ('Communication Services', 'Telecom, media, and internet platforms')
        ON CONFLICT (name) DO NOTHING;
    """)

    # 3. Tags (FK to category — name is UNIQUE on portfolio.tag)
    op.execute("""
        INSERT INTO portfolio.tag (name, description, category_id, is_active)
        VALUES
            ('ETF',        'Exchange-traded fund',                (SELECT id FROM portfolio.category WHERE name = 'Asset Type'), true),
            ('Equity',     'Individual listed stock',             (SELECT id FROM portfolio.category WHERE name = 'Asset Type'), true),
            ('Fund',       'Actively managed fund',              (SELECT id FROM portfolio.category WHERE name = 'Asset Type'), true),
            ('US',         'US-listed or US-domiciled asset',    (SELECT id FROM portfolio.category WHERE name = 'Geography'),  true),
            ('UK',         'UK-listed or UK-domiciled asset',    (SELECT id FROM portfolio.category WHERE name = 'Geography'),  true),
            ('Europe',     'European-listed asset',              (SELECT id FROM portfolio.category WHERE name = 'Geography'),  true),
            ('Global',     'Globally diversified asset',         (SELECT id FROM portfolio.category WHERE name = 'Geography'),  true),
            ('Growth',     'High-growth or momentum play',       (SELECT id FROM portfolio.category WHERE name = 'Strategy'),   true),
            ('Value',      'Undervalued or contrarian pick',     (SELECT id FROM portfolio.category WHERE name = 'Strategy'),   true),
            ('Dividend',   'Income-generating or high-yield',    (SELECT id FROM portfolio.category WHERE name = 'Strategy'),   true),
            ('AI',         'Artificial intelligence exposure',   (SELECT id FROM portfolio.category WHERE name = 'Theme'),      true),
            ('Clean Energy','Renewable and clean energy theme',  (SELECT id FROM portfolio.category WHERE name = 'Theme'),      true)
        ON CONFLICT (name) DO NOTHING;
    """)

    # 4. Sectors — no UNIQUE constraint on name; guard with WHERE NOT EXISTS
    op.execute("""
        INSERT INTO portfolio.sector (name, description, industry_id)
        SELECT s.name, s.description, i.id
        FROM (VALUES
            ('Software',              'Application and platform software',         'Technology'),
            ('Semiconductors',        'Chip design and manufacturing',             'Technology'),
            ('Hardware',              'Computers, peripherals, and electronics',   'Technology'),
            ('IT Services',           'Cloud, consulting, and managed services',   'Technology'),
            ('Pharmaceuticals',       'Drug development and distribution',         'Healthcare'),
            ('Biotechnology',         'Biologics and gene therapy',                'Healthcare'),
            ('Medical Devices',       'Diagnostics and medical equipment',         'Healthcare'),
            ('Healthcare Services',   'Hospitals, clinics, and managed care',      'Healthcare'),
            ('Banks',                 'Commercial and investment banking',          'Financials'),
            ('Insurance',             'Life, property, and casualty insurance',    'Financials'),
            ('Asset Management',      'Investment funds and wealth management',    'Financials'),
            ('Diversified Financials','Brokers, exchanges, and fintech',           'Financials'),
            ('Retail',                'Physical and e-commerce retail',            'Consumer Discretionary'),
            ('Automotive',            'Vehicle manufacturers and suppliers',       'Consumer Discretionary'),
            ('Media & Entertainment', 'Studios, streaming, and gaming',            'Consumer Discretionary'),
            ('Food & Beverages',      'Packaged food and non-alcoholic drinks',    'Consumer Staples'),
            ('Household Products',    'Personal care and cleaning products',       'Consumer Staples'),
            ('Oil & Gas',             'Exploration, production, and refining',     'Energy'),
            ('Renewable Energy',      'Solar, wind, and clean power',              'Energy'),
            ('Aerospace & Defence',   'Aircraft, missiles, and defence systems',  'Industrials'),
            ('Industrials - Other',   'Machinery, logistics, and construction',   'Industrials'),
            ('Chemicals',             'Specialty and commodity chemicals',         'Materials'),
            ('Metals & Mining',       'Steel, aluminium, and precious metals',     'Materials'),
            ('REITs',                 'Real estate investment trusts',             'Real Estate'),
            ('Telecom',               'Mobile and fixed-line operators',           'Communication Services'),
            ('Internet & Media',      'Search, social, and content platforms',    'Communication Services')
        ) AS s(name, description, industry_name)
        JOIN portfolio.industry i ON i.name = s.industry_name
        WHERE NOT EXISTS (
            SELECT 1 FROM portfolio.sector ps
            WHERE ps.name = s.name AND ps.industry_id = i.id
        );
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM portfolio.sector WHERE name IN (
            'Software', 'Semiconductors', 'Hardware', 'IT Services',
            'Pharmaceuticals', 'Biotechnology', 'Medical Devices', 'Healthcare Services',
            'Banks', 'Insurance', 'Asset Management', 'Diversified Financials',
            'Retail', 'Automotive', 'Media & Entertainment',
            'Food & Beverages', 'Household Products',
            'Oil & Gas', 'Renewable Energy',
            'Aerospace & Defence', 'Industrials - Other',
            'Chemicals', 'Metals & Mining',
            'REITs',
            'Telecom', 'Internet & Media'
        );
    """)
    op.execute("""
        DELETE FROM portfolio.tag WHERE name IN (
            'ETF', 'Equity', 'Fund',
            'US', 'UK', 'Europe', 'Global',
            'Growth', 'Value', 'Dividend',
            'AI', 'Clean Energy'
        );
    """)
    op.execute("""
        DELETE FROM portfolio.industry WHERE name IN (
            'Technology', 'Healthcare', 'Financials',
            'Consumer Discretionary', 'Consumer Staples', 'Energy',
            'Industrials', 'Materials', 'Real Estate',
            'Utilities', 'Communication Services'
        );
    """)
    op.execute("""
        DELETE FROM portfolio.category WHERE name IN (
            'Asset Type', 'Geography', 'Strategy', 'Theme'
        );
    """)
