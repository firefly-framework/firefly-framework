from __future__ import annotations

import os
import re

import yaml

import firefly.domain as ffd


class MemoryConfiguration(ffd.Configuration):
    def __init__(self, config: dict):
        super().__init__()
        self._config = config

    def _load_config(self):
        pass

    def load(self, data: str):
        path_matcher = re.compile(r'\$\{([^}^{]+)\}')

        def path_constructor(loader, node):
            value = node.value
            match = path_matcher.match(value)
            env_var = match.group()[2:-1]
            if env_var not in os.environ:
                raise ffd.ConfigurationError(f'Environment variable {env_var} is used in config, but is not set')
            return os.environ.get(env_var) + value[match.end():1]

        yaml.add_implicit_resolver('!path', path_matcher, None, yaml.SafeLoader)
        yaml.add_constructor('!path', path_constructor, yaml.SafeLoader)

        return yaml.safe_load(data)

    def save(self, data: dict):
        return yaml.dump(data)
