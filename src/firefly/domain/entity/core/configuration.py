from __future__ import annotations

from ..entity import Entity
from ..entity import dict_


class Configuration(Entity):
    _config: dict = dict_()

    @property
    def all(self):
        return self._config

    @property
    def contexts(self):
        return self._config.get('contexts', {})

    @property
    def extensions(self):
        return self._config.get('extensions', {})
