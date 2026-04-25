INSERT INTO raw.t212_history_cursor (
    endpoint,
    last_cursor,
    last_event_ts,
    updated_at
)
VALUES (
    :endpoint,
    :last_cursor,
    :last_event_ts,
    now()
)
ON CONFLICT (endpoint) DO UPDATE SET
    last_cursor   = EXCLUDED.last_cursor,
    last_event_ts = EXCLUDED.last_event_ts,
    updated_at    = now()
