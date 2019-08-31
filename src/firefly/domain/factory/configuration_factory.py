from __future__ import annotations

from abc import ABC, abstractmethod

from .factory import Factory
from ..entity.core.configuration import Configuration


class ConfigurationFactory(Factory[Configuration], ABC):
    @abstractmethod
    def __call__(self, **kwargs) -> Configuration:
        pass
