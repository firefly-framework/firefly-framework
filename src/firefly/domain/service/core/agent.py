from __future__ import annotations

from abc import ABC, abstractmethod
import firefly.domain as ffd


class Agent(ABC):
    @abstractmethod
    def handle(self, deployment: ffd.Deployment, **kwargs):
        pass
