UPDATE {target}
SET to_timestamp = CURRENT_DATE
  , is_current = false
FROM {target} as tgt
  INNER JOIN {source} src
    ON tgt.category_id = src.id
WHERE tgt.is_current = true
  AND (
      tgt.name <> src.name
    OR
      tgt.description <> src.description
  );

INSERT INTO {target} (category_id, name, description)
SELECT src.id, src.name, src.description
FROM {target} tgt
  RIGHT JOIN {source} src
    ON tgt.category_id = src.id
      AND tgt.is_current = true
WHERE tgt.category_id IS NULL;
