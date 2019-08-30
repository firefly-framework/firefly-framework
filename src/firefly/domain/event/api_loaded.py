from .framework_event import FrameworkEvent
from ..entity.entity import required


class ApiLoaded(FrameworkEvent):
    context: str = required()
