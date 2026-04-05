---
name: migrations
description: Any new or changed table requires an Alembic migration; never reference columns from unapplied migrations
---

Any new or changed table requires an Alembic migration. See `docs/03-engineering/doc-commands.md` for migration commands.

Never reference columns from unapplied migrations in application code. Confirm migrations are applied before writing code that reads those columns.

Migration files live in `migrations/postgres/versions/<schema>/`. Each schema has its own version sequence.
