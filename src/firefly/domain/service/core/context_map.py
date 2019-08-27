from __future__ import annotations

import importlib
from typing import Callable, Dict

import firefly.domain as ffd
import firefly_di as di

from ..messaging.system_bus import SystemBusAware
from ..logging.logger import LoggerAware


class ContextMap(LoggerAware, SystemBusAware):
    _config: ffd.Configuration = None
    _firefly_container: di.Container = None

    def __init__(self, bus: ffd.SystemBus):
        self._contexts: Dict[str, ffd.Context] = {}
        self._extensions: Dict[str, ffd.Extension] = {}
        self._system_bus = bus

        self._load_extensions()
        self._load_contexts()

    @property
    def contexts(self):
        return self._contexts

    @property
    def extensions(self):
        return self._extensions

    def get_context(self, name: str):
        return self._contexts[name]

    def initialize(self):
        for extension in self._extensions.values():
            extension.load_infrastructure()
        self.dispatch(ffd.ExtensionsLoaded())

        for context in self._contexts.values():
            context.load_infrastructure()
        self.dispatch(ffd.ContextsLoaded())

        for extension in self._extensions.values():
            extension.initialize()
        for context in self._contexts.values():
            context.initialize()

        for extension in self._extensions.values():
            self.dispatch(ffd.InitializationComplete(extension.name))
        for context in self._contexts.values():
            self.dispatch(ffd.InitializationComplete(context.name))

    def find_entity_by_name(self, context_name: str, entity_name: str):
        for entity in self.contexts[context_name].entities:
            if entity.__name__ == entity_name:
                return entity

    def _load_extensions(self):
        self._extensions['firefly'] = ffd.Extension('firefly', self._logger, self._config.all.get('firefly', {}),
                                                    self._system_bus, self._firefly_container)
        for name, config in self._config.extensions.items():
            if name == 'firefly':
                continue
            config = config or {}
            self._extensions[name] = ffd.Extension(name, self._logger, config, self._system_bus)
            self._extensions[name].container.register_container(self._firefly_container)
            self._firefly_container.register_container(self._extensions[name].container)

    def _load_contexts(self):
        for name, config in self._config.contexts.items():
            if name == 'firefly':
                continue
            config = config or {}
            self._contexts[name] = ffd.Context(name, self._logger, config, self._system_bus)
            self._contexts[name].container.register_container(self._firefly_container)
