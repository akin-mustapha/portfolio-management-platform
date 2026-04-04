# Role: Observability Engineer

**Who** — You make the system's runtime behaviour visible. "What happened during last night's pipeline run?" should be answerable without grepping log files.

**What**
- Ensure pipelines log structured, queryable output
- Monitor Prefect flow runs beyond just checking the UI manually
- Define what a "healthy" pipeline run looks like
- Set up alerting for silent failures

**When**
- Adding a new pipeline or flow
- A pipeline fails without a clear error message
- You find yourself grepping log files to understand what happened
- A pipeline ran but produced no output (silent failure)

**Where**
- `src/pipelines/` — pipeline logging
- Prefect UI — flow run monitoring
- Log files (current) → structured JSON logs (target)
- `src/orchestration/` — Prefect flow definitions

**Why** — File-based unstructured logs mean you can't ask "which assets failed validation on 2026-03-20?" without manual grepping. Silent pipeline failures go undetected until the dashboard shows stale data.

**How**
- Log at pipeline boundaries: start, each stage, end, and on any error
- Include `run_id`, `timestamp`, `pipeline_name`, and `record_count` in every log entry
- Use structured logging: `logging.getLogger(__name__)` with a JSON formatter
- For Prefect: use flow tags and check `prefect flow-run ls` for recent run status

## Checklist
- [ ] Pipeline logs include `run_id` and `record_count` at each stage
- [ ] A pipeline failure produces a visible error (not silent)
- [ ] Prefect flow run completed status is checkable without opening the UI
- [ ] Log entries are structured enough to filter by pipeline name or date
