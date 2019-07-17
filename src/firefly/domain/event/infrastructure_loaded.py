from dataclasses import dataclass

from .framework_event import FrameworkEvent
from ..entity.entity import required


@dataclass
class InfrastructureLoaded(FrameworkEvent):
    context: str = required()
