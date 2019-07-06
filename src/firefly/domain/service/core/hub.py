from abc import ABC, abstractmethod

from ..messaging.message_bus import MessageBusAware


class Hub(MessageBusAware, ABC):
    def __init__(self):
        self._ports = []

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def register_port(self, **kwargs):
        pass
