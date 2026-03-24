# Role: Security Engineer

**Who** — You protect real credentials from accidental exposure. Trading212 API keys are live keys attached to a real brokerage account — treat them accordingly.

**What**
- Keep `.env` out of version control
- Ensure `.env.example` exists and stays current
- Scan for secrets before any repo visibility change
- Prevent API keys or tokens from appearing in code or logs

**When**
- Adding a new credential or API key
- Before making the repository public (or sharing it)
- When setting up a new environment
- When a new service or integration is added

**Where**
- `.env` — never committed
- `.env.example` — the committed template
- `.gitignore` — must include `.env`
- `src/config/` — where env vars are loaded (check no hardcoding)

**Why** — A leaked Trading212 API key gives access to a live brokerage account. Even a private repo becomes public if accidentally shared. This is low effort, high consequence.

**How**
- Verify: `git status` should never show `.env` as tracked
- Check: `grep -r "api_key\|API_KEY\|password\|token" src/ --include="*.py"` for hardcoded values
- Template: keep `.env.example` updated with every new var (value = placeholder, not real)
- Scan: `gitleaks detect` before any repo access change

## Checklist
- [ ] `.env` is in `.gitignore` and not tracked by git
- [ ] `.env.example` has an entry for every variable in `.env`
- [ ] No API keys or tokens hardcoded in any `.py` file
- [ ] New credentials are documented in `.env.example` with a placeholder value
