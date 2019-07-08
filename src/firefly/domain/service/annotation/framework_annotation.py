from __future__ import annotations

from abc import ABC, abstractmethod


class FrameworkAnnotation(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    def __call__(self, **kwargs):
        def wrapper(cls):
            prop = []
            if hasattr(cls, self.name()):
                prop = getattr(cls, self.name())
            prop.append(kwargs)
            setattr(cls, self.name(), prop)
            return cls

        return wrapper
