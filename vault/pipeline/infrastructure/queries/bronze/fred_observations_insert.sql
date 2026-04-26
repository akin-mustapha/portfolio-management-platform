INSERT INTO {table_name} (
    id,
    series_id,
    ingested_date,
    observation_start,
    observations
)
VALUES (
    :id,
    :series_id,
    :ingested_date,
    :observation_start,
    :observations
)
