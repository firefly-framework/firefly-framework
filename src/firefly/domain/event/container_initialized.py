from .framework_event import FrameworkEvent
from ..entity.entity import required


class ContainerInitialized(FrameworkEvent):
    context: str = required()
