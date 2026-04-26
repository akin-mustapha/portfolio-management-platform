# Role: Backend Developer

**Who** — You own the services layer: the business logic that sits between the database and the dashboard. Your job is correct domain calculations, not UI or pipelines.

**What**
- Implement portfolio domain logic (returns, valuation, position sizing)
- Build and maintain service classes (`portfolio_service`, `rebalancing_service`)
- Define clean interfaces between services and the dashboard
- Keep business rules out of callbacks and pipelines

**When**
- Adding a new calculation or metric
- Wiring gold layer data to a dashboard component
- Fixing incorrect portfolio math
- A new feature requires domain logic (e.g. rebalancing engine)

**Where**
- `src/backend/services/` — service classes
- `src/shared/models/` — shared Pydantic types
- `src/dashboard/` — consumers of services (read only from here)

**Why** — If this hat is neglected, business logic bleeds into Dash callbacks. Calculations get duplicated, diverge, and become untestable.

**How**
- Services are pure functions or stateless classes — no direct DB calls in the dashboard
- Return typed Pydantic models or dataclasses, not raw dicts
- Write at least one test per service method before considering it done
- Services should not import from `src/dashboard/`

## Checklist
- [ ] Each new service method has a unit test (happy path + one failure)
- [ ] No SQL or DB calls in dashboard callbacks — go through a service
- [ ] Return types are typed (Pydantic model or typed dict)
- [ ] Service is imported by the dashboard, not the other way around
