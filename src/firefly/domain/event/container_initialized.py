from dataclasses import dataclass

from .framework_event import FrameworkEvent
from ..entity.entity import required


@dataclass
class ContainerInitialized(FrameworkEvent):
    context: str = required()
