SELECT *
FROM portfolio.asset

drop table analytics.dim_portfolio

WITH base AS (
    SELECT
        asnap.asset_id,
        asnap.data_date::date AS price_date,
        asnap.price,
        asnap.data_date,
        ROW_NUMBER() OVER (
            PARTITION BY asnap.asset_id, asnap.data_date::date
            ORDER BY asnap.data_date ASC
        ) AS rn_open,
        ROW_NUMBER() OVER (
            PARTITION BY asnap.asset_id, asnap.data_date::date
            ORDER BY asnap.data_date DESC
        ) AS rn_close
    FROM portfolio.asset_snapshot asnap
)
SELECT
    b.asset_id,
    d.id AS date_id,
    AVG(b.price) AS average_price,
    MAX(CASE WHEN b.rn_open  = 1 THEN b.price END) AS opening_price,
    MAX(CASE WHEN b.rn_close = 1 THEN b.price END) AS closing_price,
    MAX(b.price) AS high,
    MIN(b.price) AS low,
    now() AS updated_timestamp
FROM base b
JOIN analytics.dim_date d
  ON b.price_date = d.date
GROUP BY
    b.asset_id,
    d.id;


SELECT * 
FROM  analytics.dim_date
LIMIT 10


select *
from portfolio.asset_snapshot
limit 10


SELECT
*
FROM analytics.dim_asset
WHERE asset_id = 'af648241-991a-47d9-9dc0-427f235d811a'