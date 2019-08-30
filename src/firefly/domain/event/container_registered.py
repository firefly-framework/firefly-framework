from .framework_event import FrameworkEvent
from ..entity.entity import required


class ContainerRegistered(FrameworkEvent):
    context: str = required()
