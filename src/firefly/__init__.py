from typing import Tuple, List, Union

from .domain import *

EventList = Union[Event, Tuple[str, Union[dict, object]], List[Union[Event, Tuple[str, Union[dict, object]]]]]
TypeOfCommand = Union[str, Command]
TypeOfEvent = Union[str, Event]
TypeOfQuery = Union[str, Query]
