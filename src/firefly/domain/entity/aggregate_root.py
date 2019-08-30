from __future__ import annotations

from abc import ABC

from .entity import Entity


class AggregateRoot(Entity, ABC):
    pass
