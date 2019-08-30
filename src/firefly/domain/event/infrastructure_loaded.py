from .framework_event import FrameworkEvent
from ..entity.entity import required


class InfrastructureLoaded(FrameworkEvent):
    context: str = required()
