from .framework_event import framework_event
from ..entity.entity import required


@framework_event
class ApiLoaded:
    context: str = required()
