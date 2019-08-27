from dataclasses import dataclass

from .framework_event import FrameworkEvent
from ..entity.entity import required


@dataclass(eq=False, repr=False)
class DomainEntitiesLoaded(FrameworkEvent):
    context: str = required()
