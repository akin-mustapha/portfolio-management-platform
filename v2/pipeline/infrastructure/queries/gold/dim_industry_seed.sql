INSERT INTO analytics.dim_industry (id, industry_id, name, description)
SELECT
    id,
    id::TEXT   AS industry_id,
    name,
    description
FROM portfolio.industry
WHERE is_active = true
ON CONFLICT (industry_id) DO UPDATE
    SET name        = EXCLUDED.name,
        description = EXCLUDED.description
