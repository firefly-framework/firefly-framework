from dataclasses import MISSING, dataclass

from .framework_event import FrameworkEvent


@dataclass
class InitializationComplete(FrameworkEvent):
    context: str = MISSING
