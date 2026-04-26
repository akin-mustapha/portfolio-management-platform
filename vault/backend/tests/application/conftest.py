"""
Fake port implementations for application-layer tests.

One fake per port defined in application/*/ports.py.
Inject these into service constructors instead of mocks or real repos.
"""

import pytest

# ---------------------------------------------------------------------------
# portfolio ports
# ---------------------------------------------------------------------------


class FakeTableRepository:
    """Covers TableRepositoryPort — backed by a plain dict."""

    def __init__(self):
        self._store: list[dict] = []

    def select(self, params: dict) -> dict | None:
        for row in self._store:
            if all(row.get(k) == v for k, v in params.items()):
                return row
        return None

    def select_all(self) -> list:
        return list(self._store)

    def select_all_by(self, params: dict) -> list:
        return [r for r in self._store if all(r.get(k) == v for k, v in params.items())]

    def insert(self, records: list[dict]) -> None:
        self._store.extend(records)

    def upsert(self, records: list[dict], unique_key: list[str]) -> None:
        for record in records:
            key = {k: record[k] for k in unique_key}
            existing = self.select(key)
            if existing:
                existing.update(record)
            else:
                self._store.append(dict(record))

    def update(self, params: dict, data: dict) -> None:
        for row in self._store:
            if all(row.get(k) == v for k, v in params.items()):
                row.update(data)

    def delete(self, params: dict) -> None:
        self._store = [r for r in self._store if not all(r.get(k) == v for k, v in params.items())]


class FakeRepositoryFactory:
    """Covers RepositoryFactoryPort — returns a named FakeTableRepository per table."""

    def __init__(self):
        self._repos: dict[str, FakeTableRepository] = {}

    def get(self, table_name: str) -> FakeTableRepository:
        if table_name not in self._repos:
            self._repos[table_name] = FakeTableRepository()
        return self._repos[table_name]


# ---------------------------------------------------------------------------
# rebalancing ports
# ---------------------------------------------------------------------------


class FakeRebalanceConfigRepo:
    """Covers RebalanceConfigPort."""

    def __init__(self):
        self._rows: list[dict] = []
        self._asset_ids: dict[str, str] = {}

    def get_asset_id_by_ticker(self, ticker: str) -> str | None:
        return self._asset_ids.get(ticker)

    def select_all_active_with_ticker(self) -> list[dict]:
        return [r for r in self._rows if r.get("is_active", True)]

    def upsert(self, records: list[dict], unique_key: list[str]) -> None:
        for record in records:
            key = {k: record[k] for k in unique_key}
            for existing in self._rows:
                if all(existing.get(k) == v for k, v in key.items()):
                    existing.update(record)
                    break
            else:
                self._rows.append(dict(record))


class FakeRebalancePlanRepo:
    """Covers RebalancePlanPort."""

    def __init__(self):
        self._plans: list[dict] = []
        self._weights: dict[str, float] = {}

    def insert_plan(self, record: dict) -> None:
        self._plans.append(record)

    def mark_email_sent(self, plan_id: str) -> None:
        for p in self._plans:
            if p.get("id") == plan_id:
                p["email_sent"] = True

    def load_current_weights(self) -> dict[str, float]:
        return dict(self._weights)

    def get_latest(self) -> dict | None:
        return self._plans[-1] if self._plans else None


# ---------------------------------------------------------------------------
# credentials ports
# ---------------------------------------------------------------------------


class FakeCredentialsRepository:
    """Covers CredentialsPort."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def save(self, provider: str, api_key: str, secret_token: str, api_url: str) -> None:
        self._store[provider] = {
            "api_key": api_key,
            "secret_token": secret_token,
            "api_url": api_url,
        }

    def load(self, provider: str) -> dict | None:
        return self._store.get(provider)


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_repo_factory():
    return FakeRepositoryFactory()


@pytest.fixture
def fake_rebalance_config_repo():
    return FakeRebalanceConfigRepo()


@pytest.fixture
def fake_rebalance_plan_repo():
    return FakeRebalancePlanRepo()


@pytest.fixture
def fake_credentials_repo():
    return FakeCredentialsRepository()
