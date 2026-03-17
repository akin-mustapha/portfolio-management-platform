# Prefect Bugs

## Bug 1: Deploy script fails — module not found

**Error:**
```sh
scripts/deploy/prefect_deploy.sh: line 14: cd: asset_monitoring_project: No such file or directory
```

**Root cause:** Project was renamed from `asset_monitoring_project` to `src`. Deploy script wasn't updated.

**Fix:** Updated `/scripts/deploy/prefect_deploy.sh` to use `src` as the directory name.

---

## Bug 2: Prefect server hangs on start

**Symptom:** Server starts but hangs — UI doesn't load at `localhost:4200`.

**Fix:** Kill the process holding port 4200, then restart.

```sh
lsof -nP -iTCP:4200 -sTCP:LISTEN
kill -9 <process-id>
prefect server start
```

If that doesn't work, full reset:
```sh
prefect server stop
rm -rf ~/.prefect
prefect server start
```
