from typing import Tuple, List, Union, Type

from .domain import *

EventList = Union[Event, Tuple[str, Union[dict, object]], List[Union[Event, Tuple[str, Union[dict, object]]]]]
TypeOfCommand = Union[str, Type[Command]]
TypeOfEvent = Union[str, Type[Event]]
TypeOfQuery = Union[str, Type[Query]]
