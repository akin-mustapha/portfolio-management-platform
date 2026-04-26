from pathlib import Path


def load_query(path: Path) -> str:
    """Read a .sql file and return its contents as a string."""
    return path.read_text()
