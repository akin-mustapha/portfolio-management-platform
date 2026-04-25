INSERT INTO analytics.dim_sector (id, sector_id, industry_id, name, description)
SELECT
    ps.id,
    ps.id::TEXT                AS sector_id,
    di.id                      AS industry_id,
    ps.name,
    ps.description
FROM portfolio.sector ps
JOIN analytics.dim_industry di ON di.id = ps.industry_id
WHERE ps.is_active = true
ON CONFLICT (sector_id) DO UPDATE
    SET name        = EXCLUDED.name,
        description = EXCLUDED.description,
        industry_id = EXCLUDED.industry_id
