SELECT
    id                AS snapshot_id,
    ingested_timestamp,
    ingested_date,
    account_data,
    position_data
FROM raw.t212_snapshot
WHERE processed_at IS NULL
  AND ingested_date >= (
      SELECT COALESCE(MAX(data_timestamp::DATE), '1900-01-01')
      FROM staging.asset
  )
ORDER BY ingested_timestamp ASC
