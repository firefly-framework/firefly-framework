from __future__ import annotations

from typing import List

import firefly.domain as ffd
import firefly_di as di

from ..aggregate_root import AggregateRoot
from ..entity import list_, hidden


class ContextMap(AggregateRoot):
    contexts: List[ffd.Context] = list_()
    extensions: List[ffd.Extension] = list_()
    _config: ffd.Configuration = hidden()
    _firefly_container: di.Container = hidden()

    def __post_init__(self):
        for name, config in self._config.extensions.items():
            self.extensions.append(ffd.Extension(name=name, config=config))
        for name, config in self._config.contexts.items():
            self.contexts.append(ffd.Context(name=name, config=config))

    def get_context(self, name: str):
        for context in self.contexts:
            if context.name == name:
                return context

    def get_extension(self, name: str):
        for extension in self.extensions:
            if extension.name == name:
                return extension

    # def initialize(self):
    #     events = []
    #
    #     for extension in self._extensions.values():
    #         extension.load_infrastructure()
    #     events.append(ffd.ExtensionsLoaded())
    #
    #     for context in self._contexts.values():
    #         context.load_infrastructure()
    #     events.append(ffd.ContextsLoaded())
    #
    #     for extension in self._extensions.values():
    #         extension.initialize()
    #     for context in self._contexts.values():
    #         context.initialize()
    #
    #     for extension in self._extensions.values():
    #         events.append(ffd.InitializationComplete(extension.name))
    #     for context in self._contexts.values():
    #         events.append(ffd.InitializationComplete(context.name))
    #
    #     return events

    def find_entity_by_name(self, context_name: str, entity_name: str):
        for entity in self.get_context(context_name).entities:
            if entity.__name__ == entity_name:
                return entity

    # def _load_extensions(self):
    #     self._extensions['firefly'] = ffd.Extension('firefly', self._logger, self._config.all.get('firefly', {}),
    #                                                 self._system_bus, self._firefly_container)
    #     for name, config in self._config.extensions.items():
    #         if name == 'firefly':
    #             continue
    #         config = config or {}
    #         self._extensions[name] = ffd.Extension(name, self._logger, config, self._system_bus)
    #         self._extensions[name].container.register_container(self._firefly_container)
    #         self._firefly_container.register_container(self._extensions[name].container)
    #
    # def _load_contexts(self):
    #     for name, config in self._config.contexts.items():
    #         if name == 'firefly':
    #             continue
    #         config = config or {}
    #         self._contexts[name] = ffd.Context(name, self._logger, config, self._system_bus)
    #         self._contexts[name].container.register_container(self._firefly_container)
