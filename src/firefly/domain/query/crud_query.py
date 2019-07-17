from __future__ import annotations

from dataclasses import dataclass

from ..entity.messaging.query import Query


@dataclass
class CrudQuery(Query):
    pass
