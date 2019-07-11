from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Callable


class FrameworkAnnotation(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    def __call__(self, child_callback: Callable = None, **kwargs):
        def wrapper(cls):
            prop = []
            if hasattr(cls, self.name()):
                prop = getattr(cls, self.name())
            prop.append(self._callback(cls, kwargs))
            setattr(cls, self.name(), prop)

            if child_callback is not None and inspect.isclass(cls):
                for k, v in cls.__dict__.items():
                    if hasattr(v, self.name()):
                        child_callback(cls, v)

            return cls

        return wrapper

    @staticmethod
    def _callback(cls, kwargs):
        return kwargs
