from dataclasses import dataclass

from .framework_event import FrameworkEvent
from ..entity import required


@dataclass
class InitializationComplete(FrameworkEvent):
    context: str = required()
