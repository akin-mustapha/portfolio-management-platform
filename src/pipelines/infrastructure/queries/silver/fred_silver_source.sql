SELECT
    f.id               AS raw_id,
    f.series_id,
    f.ingested_date,
    obs->>'date'       AS observation_date,
    obs->>'value'      AS observation_value
FROM raw.fred_observations f,
     jsonb_array_elements(f.observations) AS obs
WHERE f.processed_at IS NULL
  AND obs->>'value' != '.'
ORDER BY f.series_id, observation_date ASC;
