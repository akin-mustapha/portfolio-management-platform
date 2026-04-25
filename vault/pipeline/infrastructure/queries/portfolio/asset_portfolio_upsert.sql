MERGE INTO {destination_table_name} AS tgt
USING
  (
    VALUES
      {values}
  )
AS src (ticker, name, broker, currency)
ON    tgt.ticker = src.ticker
  AND tgt.broker = src.broker
  AND tgt.currency = src.currency
WHEN NOT MATCHED THEN
  INSERT (ticker, name, broker, currency)
  VALUES (src.ticker, src.name, src.broker, src.currency)
WHEN MATCHED AND tgt.name <> src.name THEN
UPDATE
  SET   name = src.name
      , updated_timestamp = NOW()
WHEN NOT MATCHED BY SOURCE THEN
  UPDATE
    SET to_timestamp = NOW();
