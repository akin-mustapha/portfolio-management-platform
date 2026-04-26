CREATE TABLE IF NOT EXISTS {partition_name}
PARTITION OF {table_name}
FOR VALUES FROM (:day) TO (:next_day);
