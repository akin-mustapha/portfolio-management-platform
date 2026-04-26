SELECT ticker, name, broker, currency
FROM (
    SELECT *,
          ROW_NUMBER() OVER (
              PARTITION BY ticker, broker, currency
              ORDER BY data_timestamp DESC
          ) as rn
    FROM staging.asset
) t
WHERE rn = 1;
