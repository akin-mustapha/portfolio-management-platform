from typing import Protocol

class Source(Protocol):
  def fetch(self):
    raise NotImplementedError