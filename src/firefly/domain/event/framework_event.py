from __future__ import annotations

from abc import ABC

from ..entity.messaging.event import Event
from ..utils import generate_dc


class FrameworkEvent(Event, ABC):
    pass


def framework_event(_cls=None, **kwargs):
    return generate_dc(FrameworkEvent, _cls, **kwargs)
