"""
Docstring for src.services.event_producer.domain
This module contains the domain models for the event producer service. It defines the Event dataclass which represents an event that can be produced and sent to a destination. The Event dataclass has three fields: name, payload, and datetime. The name field is a string that represents the name of the event, the payload field is a dictionary that contains the data associated with the event, and the datetime field is a date object that represents the time when the event was created.
"""
from dataclasses import dataclass
from datetime import date

@dataclass
class Event:
  name: str
  payload: dict
  datetime: date
  
  def __iter__(self):
    # This allows us to convert the Event dataclass to a dictionary using dict(event)
    yield from self.__dict__.items()