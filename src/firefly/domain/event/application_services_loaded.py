from .framework_event import FrameworkEvent
from ..entity.entity import required


class ApplicationServicesLoaded(FrameworkEvent):
    context: str = required()
