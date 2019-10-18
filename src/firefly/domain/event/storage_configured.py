from .framework_event import FrameworkEvent
from ..entity.entity import required


class StorageConfigured(FrameworkEvent):
    context: str = required()
