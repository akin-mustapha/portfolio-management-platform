import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

_HERE = Path(__file__).parent


@dataclass(frozen=True)
class Tranche:
    drawdown_pct: float
    order_value: float


@dataclass(frozen=True)
class Asset:
    name: str
    ticker: str
    tranches: tuple[Tranche, ...]


def _load_watchlist() -> tuple[list[Asset], float]:
    with open(_HERE / "watchlist.yaml") as f:
        raw = yaml.safe_load(f)

    monthly_limit = float(raw.get("monthly_limit", 0.0))

    assets = []
    for item in raw.get("assets", []):
        tranches = tuple(
            Tranche(
                drawdown_pct=float(t["drawdown_pct"]),
                order_value=float(t["order_value"]),
            )
            for t in item.get("tranches", [])
        )
        assets.append(Asset(name=item["name"], ticker=item["ticker"], tranches=tranches))
    return assets, monthly_limit


DATABASE_URL: str = os.environ["DATABASE_URL"]
API_URL: str = os.environ["API_URL"]
API_TOKEN: str = os.environ["API_TOKEN"]
SECRET_TOKEN: str = os.environ["SECRET_TOKEN"]
DRY_RUN: bool = os.getenv("DRY_RUN", "false").lower() == "true"

ASSETS: list[Asset]
MONTHLY_LIMIT: float
ASSETS, MONTHLY_LIMIT = _load_watchlist()
