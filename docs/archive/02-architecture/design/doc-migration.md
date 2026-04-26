---
name: Database Migration
description: Documentation on database migration
---

# Database Migration

## Overview

Schema migrations are managed with [Alembic](https://alembic.sqlalchemy.org/). Migrations are split into four independent tracks — one per medallion layer — so each layer can evolve without coupling to the others.

---

## Migration Tracks

| Track ini | Schema | Layer | Versions directory |
| --------- | ------ | ----- | ------------------ |
| `raw.ini` | `raw` | Bronze | `migrations/postgres/versions/raw/` |
| `staging.ini` | `staging` | Silver | `migrations/postgres/versions/staging/` |
| `analytics.ini` | `analytics` | Gold | `migrations/postgres/versions/analytics/` |
| `portfolio.ini` | `portfolio` | OLTP | `migrations/postgres/versions/portfolio/` |

All tracks share the same `env.py` and `script.py.mako` at `migrations/postgres/`. Each track stores its Alembic state in its own schema (e.g. `raw.alembic_version`) to avoid collision.

---

## Rules

- **One layer per migration.** A staging change goes into the `staging` track. Never mix schemas in the same migration.
- **Every schema change needs a migration.** Do not alter tables manually — always write a migration and apply it through Alembic.
- **Migrations are append-only.** Do not edit an existing migration once it has been applied to any environment. Write a new one instead.

---

## Common Commands

See `docs/03-engineering/doc-commands.md` for the full command reference.

### Apply all tracks (fresh database)

```sh
alembic -c migrations/postgres/portfolio.ini upgrade head
alembic -c migrations/postgres/raw.ini upgrade head
alembic -c migrations/postgres/staging.ini upgrade head
alembic -c migrations/postgres/analytics.ini upgrade head
```

### Create a new migration

```sh
# Replace staging.ini with the ini file for the layer you are changing
alembic -c migrations/postgres/staging.ini revision -m "describe_the_change"
```

This generates a new file in `migrations/postgres/versions/staging/`. Fill in the `upgrade()` and `downgrade()` functions before applying.

### Apply a track

```sh
alembic -c migrations/postgres/staging.ini upgrade head
```

### Check track status

```sh
alembic -c migrations/postgres/staging.ini current
```

---

## File Structure

```text
migrations/
  postgres/
    env.py                   ← shared; reads version_table_schema from ini
    script.py.mako           ← shared template
    raw.ini                  ← Bronze track config
    staging.ini              ← Silver track config
    analytics.ini            ← Gold track config
    portfolio.ini            ← OLTP track config
    versions/
      raw/                   ← Bronze migrations
      staging/               ← Silver migrations
      analytics/             ← Gold migrations
      portfolio/             ← OLTP migrations
  sqlite/                    ← Local/test database (separate system)
```

---

## How the Version Table Works

Alembic tracks which migrations have been applied in a version table. Each track writes to its own schema:

| Track | Version table |
| ----- | ------------- |
| raw | `raw.alembic_version` |
| staging | `staging.alembic_version` |
| analytics | `analytics.alembic_version` |
| portfolio | `portfolio.alembic_version` |

This is configured via the `version_table_schema` key in each ini file and read by `env.py`.

---

## Stamping an Existing Database

If the database already has the schema applied (e.g. restored from backup, or migrating from the old single-track setup), use `stamp` to record the current head without re-running SQL:

```sh
alembic -c migrations/postgres/raw.ini stamp <head-revision-id>
```

Get the head revision ID with:

```sh
alembic -c migrations/postgres/raw.ini heads
```
