from __future__ import annotations

from abc import ABC, abstractmethod


class FrameworkAnnotation(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    def __call__(self, **kwargs):
        def wrapper(cls):
            setattr(cls, self.name(), kwargs)
            return cls

        return wrapper
