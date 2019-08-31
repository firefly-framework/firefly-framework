from __future__ import annotations

import firefly.domain as ffd
from firefly.domain.entity.core.configuration import Configuration


class MemoryConfigurationFactory(ffd.ConfigurationFactory):
    def __call__(self, config: dict) -> Configuration:
        return Configuration(_config=config)
