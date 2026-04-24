"""
Re-export shim — routes T212Client to the shared Trading212APIClient.

Keeps scheduler.py and strategy.py import-compatible while consolidating
the actual implementation in src/pipelines/infrastructure/clients/.
"""
import sys
from pathlib import Path

# Make the project root importable so the shared client can be used standalone.
_ROOT = Path(__file__).parent.parent.parent / "src"
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# The shared client uses relative imports internally; load it via its package path.
from pipelines.infrastructure.clients.api_client_trading212 import Trading212APIClient as T212Client  # noqa: E402, F401

__all__ = ["T212Client"]
