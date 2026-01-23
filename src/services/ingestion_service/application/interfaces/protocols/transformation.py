from typing import Protocol, Iterable, Any

class Transformation(Protocol):
  def apply_to(self, records: Iterable[Any]) -> Iterable[Any]:
    raise NotImplementedError