from __future__ import annotations

from typing import List

from .queue import Queue
from ..entity import Entity, id_, list_


class Forwarder(Entity):
    name: str = id_()
    subscribers: List[Queue] = list_()
