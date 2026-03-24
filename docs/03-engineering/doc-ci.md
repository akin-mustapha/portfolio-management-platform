# Continues integration

## Linting

Project use Ruff lint to check for error and ensure code consistency

## Get started

**Installation:**

Add to requirements.txt

```sh
ruff
```

**Add Linting Step:** To [ci workflow](.github/workflows/ci.yml)

```YML
      - name: Run Linter
        run: |
          ruff check .
```

**Look UP Error:**

```sh
ruff rule F821
```

**Apply Fix:**

```sh
ruff check --fix
```

## Formatting

```yaml
      - name: Run Formatter
        run: |
          python3 -m black src/

```
