"""Date-aware JSON serialization helpers for FastAPI responses."""

import json
from datetime import date, datetime
from decimal import Decimal

from fastapi.responses import JSONResponse


def _default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _normalize_keys(obj):
    """Recursively convert non-string dict keys (e.g. date) to strings."""
    if isinstance(obj, dict):
        return {
            (k.isoformat() if isinstance(k, (date, datetime)) else k): _normalize_keys(
                v
            )
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_normalize_keys(i) for i in obj]
    return obj


def date_response(data) -> JSONResponse:
    """Return a JSONResponse that correctly serializes date/datetime/Decimal values."""
    content = json.loads(json.dumps(_normalize_keys(data), default=_default))
    return JSONResponse(content=content)
