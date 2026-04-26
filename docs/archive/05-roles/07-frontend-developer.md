# Role: Frontend Developer

**Who** — You build the Dash dashboard. Your job is a clear, usable interface that answers portfolio questions — not the most feature-rich chart library demo.

**What**
- Build and maintain Dash layouts and components
- Write callbacks that connect UI to services
- Apply the project theme (dark mode, color tokens)
- Ensure layouts are clear and load without errors

**When**
- Adding a new chart or component
- Fixing a layout or dark mode issue
- Wiring a new service output to a visual
- A callback raises a duplicate Output error

**Where**
- `src/dashboard/` — all dashboard code
- `/assets/` — CSS and theme files
- `docs/02-architecture/design/ui-design.md` — dashboard questions and layout intent

**Why** — Duplicate Output IDs crash the app silently. Unchecked theme tokens produce broken dark mode. Callbacks that call the DB directly bypass the service layer and become untestable.

**How**
- Before adding a callback Output, search `Output('component-id'` across the dashboard to confirm it doesn't already exist
- Use theme tokens and `ct` variables — do not hardcode hex colors
- Confirm layout direction (side-by-side vs stacked) with yourself or the product hat before implementing
- Keep callbacks thin — call a service, pass result to the component

## Checklist
- [ ] No duplicate `Output('component-id', ...)` in any callback
- [ ] Dark mode renders correctly (check both themes)
- [ ] Callback calls a service — no direct DB or pipeline logic inside it
- [ ] New component has a stable, unique ID (not auto-generated)
