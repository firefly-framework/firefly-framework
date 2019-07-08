from .framework_event import FrameworkEvent


class ContainerRegistered(FrameworkEvent):
    def __init__(self, context: str):
        super().__init__(body=context)
