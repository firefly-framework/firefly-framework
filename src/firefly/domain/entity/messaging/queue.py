from __future__ import annotations

from typing import List

from firefly.domain.entity.entity import Entity, id_, list_

from ..core.context import Context


class Queue(Entity):
    name: str = id_()
    subscribers: List[Context] = list_()
