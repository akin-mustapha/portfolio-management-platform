UPDATE {target}
SET to_timestamp = CURRENT_DATE
  , is_current = false
FROM {target} as tgt
  INNER JOIN {source} src
    ON tgt.tag_id = src.id
WHERE tgt.is_current = true
  AND (
      tgt.name <> src.name
    OR
      tgt.category_id <> src.category_id
    OR
      tgt.description <> src.description
  );

INSERT INTO {target} (tag_id, name, description, category_id)
SELECT src.id, src.name, src.description, src.category_id
FROM {target} tgt
  RIGHT JOIN {source} src
    ON tgt.tag_id = src.id
      AND tgt.is_current = true
WHERE tgt.tag_id IS NULL;
