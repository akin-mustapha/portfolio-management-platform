INSERT INTO {table_name} (
    id
  , ingested_date
  , account_data
  , position_data
)
VALUES ((:id), (:ingested_date), (:account_data), (:position_data))
