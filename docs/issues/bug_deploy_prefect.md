# Deploy Prefect Bug

Missing asset_monitoring_project module in prefect deployment bash script.

## Steps

**run**:

```sh
scripts/deploy/prefect_deploy.sh

```

**Error**:

```sh
[notice] A new release of pip is available: 25.2 -> 26.0.1
[notice] To update, run: pip install --upgrade pip
Changing directory to asset_monitoring_project...
scripts/deploy/prefect_deploy.sh: line 14: cd: asset_monitoring_project: No such file or directory
```

## Comment

asset_monitoring_project renamed to src

## Fix

Update `/scripts/deploy/prefect_deploy.sh`
