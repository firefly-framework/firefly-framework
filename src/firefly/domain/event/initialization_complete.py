from .framework_event import FrameworkEvent
from ..entity import required


class InitializationComplete(FrameworkEvent):
    context: str = required()
