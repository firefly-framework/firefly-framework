from __future__ import annotations

from ..entity import Entity
from ..entity import dict_


class Configuration(Entity):
    _config: dict = dict_()

    def __post_init__(self):
        if self._config is None:
            self._config = {}

    @property
    def all(self):
        return self._config

    @property
    def contexts(self):
        return self._config.get('contexts', {})

    @property
    def environments(self):
        return self._config.get('environments', {})
