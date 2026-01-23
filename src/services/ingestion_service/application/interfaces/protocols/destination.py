from typing import Protocol

class Destination(Protocol):
  def save(self):
    raise NotImplementedError