from __future__ import annotations

from typing import Dict

from firefly.domain.factory.factory import T

from .factory import Factory
from ..error import ConfigurationError
from ..service.core.agent import Agent


class AgentFactory(Factory[Agent]):
    def __init__(self, agents: Dict[str, Agent]):
        self._agents = agents

    def __call__(self, provider: str) -> T:
        if provider not in self._agents:
            raise ConfigurationError(f'No agent registered for provider "{provider}"')
        return self._agents[provider]

    def register(self, provider: str, agent: Agent):
        self._agents[provider] = agent
