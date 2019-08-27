from .framework_event import framework_event
from ..entity import required


@framework_event
class InitializationComplete:
    context: str = required()
