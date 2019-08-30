from .framework_event import FrameworkEvent
from ..entity.entity import required


class DomainEntitiesLoaded(FrameworkEvent):
    context: str = required()
