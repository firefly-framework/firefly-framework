from dataclasses import dataclass

from .framework_event import FrameworkEvent
from ..entity.entity import required


@dataclass
class ApiLoaded(FrameworkEvent):
    context: str = required()
