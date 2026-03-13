Skills Setup Plan
                                                                                                                                                
     Recommendation on proposed skill set
                                                                                                                                                
     All 6 proposed skills are solid. One note: refresh-schema-doc already exists (empty) — doc-refresh will supersede it. Rename             
     recommendation: keep build as-is per user intent, the description will clarify it's backend/generic Python.                              

     ---
     Files to Create (6 new SKILL.md files)

     - .claude/skills/product-manager/SKILL.md
       - Trigger: feature scoping, requirements, backlog, user stories, product decisions
       - Context: Individual investor persona, Trading212 integration, portfolio monitoring use cases
       - References: docs/01-product/business-requirements.md, docs/01-product/product-requirements.md, docs/wiki.md
     - .claude/skills/product-architect/SKILL.md
       - Trigger: system design, architecture decisions, data model, schema design, service boundaries, integration patterns
       - Context: Event-driven architecture, medallion layers (raw→staging→analytics), Kimball gold layer, service ownership
       - References: docs/02-architecture/architecture.md, all docs/02-architecture/design/ docs and schemas
     - .claude/skills/build-ui/SKILL.md
       - Trigger: building/editing dashboard pages, Dash components, layouts, callbacks, charts
       - Context: Dash + Dash Bootstrap + Dash AG Grid + Dash Design Kit; two pages (Portfolio, Asset); src/dashboard/ structure
       - References: src/dashboard/ layout conventions, page pattern at src/dashboard/core/pages/
     - .claude/skills/build/SKILL.md
       - Trigger: building/editing Python backend — services, domain models, repositories, shared utilities, configs
       - Context: Python 3, FastAPI, SQLModel, Pydantic, Alembic migrations, repository pattern; src/services/, src/shared/, src/config/
       - References: docs/02-architecture/design/doc-services.md, docs/02-architecture/design/doc-migration.md
     - .claude/skills/build-pipeline/SKILL.md
       - Trigger: building/editing data ingestion, Kafka event flow, Prefect orchestration, Trading212 API integration
       - Context: Event producer (Trading212 → Kafka) + event consumer (Kafka → PostgreSQL raw); Prefect flows in src/orc/; src/ingestion/
       - References: docs/02-architecture/design/doc-pipelines.md, docs/02-architecture/design/pipelines/
     - .claude/skills/doc-refresh/SKILL.md
       - Trigger: after code changes, when asked to update docs or keep skills in sync
       - Context: Maps code areas to their owning docs; covers when to update which skill file
       - Change map: schema change → schema-*.md + database skill + financial-analyst skill; pipeline change → doc-pipelines.md; service change
     → doc-services.md; new metric → doc-metrics.md + financial-analyst skill; UI change → product docs + build-ui skill
       - Also fill in empty refresh-schema-doc/SKILL.md or deprecate it

     Verification
