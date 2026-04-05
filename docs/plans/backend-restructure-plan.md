# Backend Restructure Plan — DDD Layout

## Goal

Restructure `src/backend/` to follow a domain-driven layout: layers at the top, domains as subdivisions within each layer. Remove the `services/` wrapper. Keep everything outside `src/backend/` untouched.

---

## Target Structure

```
src/backend/
├── domain/
│   ├── portfolio/          ← Asset (root), Tag, Category, AssetTag, Industry, Sector + repo interfaces + value objects
│   └── rebalancing/        ← RebalanceConfig (root), RebalancePlan (root) + repo interfaces + value objects
├── application/
│   ├── portfolio/          ← PortfolioService, application interfaces
│   └── rebalancing/        ← RebalancingService, plan_generator
└── infrastructure/
    ├── portfolio/          ← asset, tag, category, asset_tag, sector, industry repos + factory
    ├── rebalancing/        ← rebalance_config, rebalance_plan repos + factory
    └── credentials/        ← CredentialsRepository (no domain entity — pure infra)
```

---

## Aggregate Roots

### `portfolio` domain

**`Asset`** is the aggregate root. `Tag`, `AssetTag`, `Industry`, `Sector`, and `Category` exist only in relation to assets. External code must not manipulate `AssetTag` directly — that association is managed through `Asset`.

Practical consequence: repositories are defined per aggregate root. `AssetTagRepository` is a current implementation detail; it should eventually move behind `AssetRepository`. Not a blocker for this restructure.

### `rebalancing` domain

Two aggregate roots:

- **`RebalanceConfig`** — defines the rebalancing rules for a single asset. It is the root for config mutations.
- **`RebalancePlan`** — represents the full portfolio plan at a point in time. It is not owned by a single config, so it is its own root.

Each aggregate root has exactly one repository interface defined in the domain layer.

---

## Value Objects

Value objects are immutable, validated on construction, and defined in their domain's `value_objects.py`. Two with identical data are equal.

### `domain/portfolio/value_objects.py`

| Value Object | Wraps | Invariant |
|---|---|---|
| `Ticker` | `str` | non-empty, uppercased |
| `Currency` | `str` | non-empty, 3 chars, uppercased (ISO 4217) |
| `Broker` | `str` | non-empty string |

`Asset.ticker` → `Ticker`, `Asset.currency` → `Currency`, `Asset.broker` → `Broker`.

### `domain/rebalancing/value_objects.py`

| Value Object | Wraps | Invariant |
|---|---|---|
| `WeightBand` | `(target, min, max): float` | `min ≤ target ≤ max`, all in `[0.0, 1.0]` |
| `RebalanceThreshold` | `float` | `> 0.0` |
| `PlanStatus` | `str` (enum) | constrained to known values: `pending`, `active`, `completed`, `cancelled` |

`RebalanceConfig.target_weight_pct` / `min_weight_pct` / `max_weight_pct` → replaced by a single `WeightBand`.
`RebalanceConfig.rebalance_threshold_pct` → `RebalanceThreshold`.
`RebalancePlan.status` → `PlanStatus`.

`WeightBand` is the most important: it groups three fields that only make sense together and encodes the invariant that target must sit within the band as a single validated unit.

---

## File Mapping

### domain/

| From | To |
|---|---|
| `services/portfolio/domain/entities.py` | `domain/portfolio/entities.py` |
| `services/portfolio/application/interfaces.py` | `domain/portfolio/interfaces.py` |
| `services/rebalancing/domain/entities.py` | `domain/rebalancing/entities.py` |
| _(new)_ | `domain/portfolio/value_objects.py` — `Ticker`, `Currency`, `Broker` |
| _(new)_ | `domain/rebalancing/value_objects.py` — `WeightBand`, `RebalanceThreshold`, `PlanStatus` |

### application/

| From | To |
|---|---|
| `services/portfolio/service.py` | `application/portfolio/service.py` |
| `services/portfolio/portfolio_service_builder.py` | `application/portfolio/factory.py` |
| `services/rebalancing/service.py` | `application/rebalancing/service.py` |
| `services/rebalancing/rebalancing_service_builder.py` | `application/rebalancing/factory.py` |
| `services/rebalancing/plan_generator.py` | `application/rebalancing/plan_generator.py` |

### infrastructure/

| From | To |
|---|---|
| `services/portfolio/infrastructure/repositories/asset_repository.py` | `infrastructure/portfolio/asset_repository.py` |
| `services/portfolio/infrastructure/repositories/tag_repository.py` | `infrastructure/portfolio/tag_repository.py` |
| `services/portfolio/infrastructure/repositories/category_repository.py` | `infrastructure/portfolio/category_repository.py` |
| `services/portfolio/infrastructure/repositories/asset_tag_repository.py` | `infrastructure/portfolio/asset_tag_repository.py` |
| `services/portfolio/infrastructure/repositories/industry_repository.py` | `infrastructure/portfolio/industry_repository.py` |
| `services/portfolio/infrastructure/repositories/sector_repository.py` | `infrastructure/portfolio/sector_repository.py` |
| `services/portfolio/infrastructure/repositories/repository_factory.py` | `infrastructure/portfolio/repository_factory.py` |
| `services/portfolio/infrastructure/repositories/base_table_repository.py` | deleted — it is a re-export from `shared/repositories/base_table_repository.py` |
| `services/rebalancing/infrastructure/repositories/rebalance_config_repository.py` | `infrastructure/rebalancing/rebalance_config_repository.py` |
| `services/rebalancing/infrastructure/repositories/rebalance_plan_repository.py` | `infrastructure/rebalancing/rebalance_plan_repository.py` |
| `services/rebalancing/infrastructure/repositories/repository_factory.py` | `infrastructure/rebalancing/repository_factory.py` |
| `services/credentials/repository.py` | `infrastructure/credentials/repository.py` |

---

## Import Changes

Every internal import changes from `backend.services.<domain>.*` to `backend.<layer>.<domain>.*`.

### Key callsites outside backend/ to update:

| File | Old import | New import |
|---|---|---|
| `dashboard/controllers/asset_controller.py` | `backend.services.portfolio.*` | `backend.application.portfolio.*` |
| `dashboard/controllers/asset_profile_controller.py` | `backend.services.portfolio.*` | `backend.application.portfolio.*` |
| `dashboard/controllers/portfolio_controller.py` | `backend.services.portfolio.*` | `backend.application.portfolio.*` |
| `dashboard/pages/portfolio/callbacks/rebalancing.py` | `backend.services.rebalancing.*` | `backend.application.rebalancing.*` |
| `dashboard/api/credentials_routes.py` | `backend.services.credentials.*` | `backend.infrastructure.credentials.*` |
| `orchestration/prefect/flow_rebalance_plan.py` | `backend.services.rebalancing.*` | `backend.application.rebalancing.*` |

> After moving, grep for any remaining `backend.services` references to catch stragglers.

---

## What Does Not Change

- `shared/repositories/base_table_repository.py` — stays in shared; all repos continue to inherit from it
- `shared/utils/`, `shared/database/`, `shared/notifications/` — untouched
- `src/pipelines/`, `src/dashboard/`, `src/orchestration/` — untouched
- No Alembic migrations needed — this is a code reorganisation only, no schema changes

---

## Steps

1. Create the new directory tree under `src/backend/`
2. Write `domain/portfolio/value_objects.py` — `Ticker`, `Currency`, `Broker`
3. Write `domain/rebalancing/value_objects.py` — `WeightBand`, `RebalanceThreshold`, `PlanStatus`
4. Move files per the mapping table above
5. Update `Asset` to use `Ticker`, `Currency`, `Broker`; update `to_record()` to unpack them
6. Update `RebalanceConfig` to replace the three weight `float` fields with `WeightBand` and `rebalance_threshold_pct` with `RebalanceThreshold`; update `to_record()` to unpack them
7. Update `RebalancePlan.status` to use `PlanStatus`; update `to_record()` accordingly
8. Update all internal imports within `backend/` to use the new paths
9. Update all external imports (dashboard, orchestration) per the callsite table
10. Delete `services/portfolio/infrastructure/repositories/base_table_repository.py`
11. Delete the now-empty `services/` tree
12. Run the test suite and verify imports resolve in both dashboard and Prefect contexts

---

## Notes

- `credentials` has no domain entity — it is purely infra, so it lives only under `infrastructure/credentials/`
- The two `_service_builder.py` files are renamed to `factory.py` — they are factories, not builders
- `domain/portfolio/interfaces.py` holds the `AssetQueryRepository` protocol — this belongs in domain (it is a repository interface, not an application contract)
