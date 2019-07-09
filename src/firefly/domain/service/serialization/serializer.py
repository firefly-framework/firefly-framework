from __future__ import annotations

from abc import ABC, abstractmethod


class Serializer(ABC):
    @abstractmethod
    def serialize(self, data):
        pass

    @abstractmethod
    def deserialize(self, data):
        pass
