/*
  what is the difference between 

  recent_high_30d vs high


  - TODO
  validate high is tody

*/


;WITH most_recent_asset AS
(
  SELECT
      ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY data_timestamp DESC) as rn
    , id
  FROM staging.asset
)
SELECT 
    t1.ticker
  , t1.name
  , t1.price
  , t1.avg_price
  , t1.cost
  , t1.profit 
  , t1.fx_impact
  , t3.*
FROM staging.asset t1
  INNER JOIN most_recent_asset t2
    ON t1.id = t2.id
  INNER JOIN staging.asset_computed t3
    ON t1.id = t3.asset_id
WHERE t2.rn = 1
ORDER BY "profit" desc