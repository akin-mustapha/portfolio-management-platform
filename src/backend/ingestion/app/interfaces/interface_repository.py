try:
    from src.shared.repositories.interface import RepositoryInterface as Repository
except ImportError:
    from shared.repositories.interface import RepositoryInterface as Repository

__all__ = ["Repository"]
