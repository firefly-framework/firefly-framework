from __future__ import annotations

from abc import ABC

import firefly.domain as ffd

from .entity import Entity


class AggregateRoot(Entity, ABC):
    pass


def aggregate_root(_cls=None, **kwargs) -> AggregateRoot:
    return ffd.generate_dc(AggregateRoot, _cls, **kwargs)
