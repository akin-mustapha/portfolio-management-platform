INSERT INTO {table_name} (
    id,
    ingested_date,
    payload
)
VALUES (
    :id,
    :ingested_date,
    :payload
)
ON CONFLICT (id, ingested_date) DO NOTHING
