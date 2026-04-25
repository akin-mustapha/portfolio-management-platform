SELECT MAX(observation_date) AS max_date
FROM staging.fred_observation
WHERE series_id = :series_id
