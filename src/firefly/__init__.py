from typing import Tuple, List

from .domain import *

CommandResponse = Union[Event, Tuple[str, Union[dict, object]], List[Union[Event, Tuple[str, Union[dict, object]]]]]
