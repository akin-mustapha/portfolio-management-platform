UPDATE {target}
SET to_timestamp = CURRENT_DATE
  , is_current = false
FROM {target} as tgt
    LEFT JOIN {source} src
    ON tgt.asset_id = src.asset_id
    AND tgt.tag_id = src.tag_id
WHERE tgt.is_current = true
  AND tgt.id IS NULL;

INSERT INTO {target} (asset_id, tag_id)
SELECT src.asset_id, src.tag_id
FROM {target} tgt
  RIGHT JOIN {source} src
      ON tgt.asset_id = src.asset_id
      AND tgt.tag_id = src.tag_id
      AND tgt.is_current = true
WHERE tgt.tag_id IS NULL AND tgt.asset_id IS NULL;
