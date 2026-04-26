SELECT last_cursor, last_event_ts
FROM raw.t212_history_cursor
WHERE endpoint = :endpoint
