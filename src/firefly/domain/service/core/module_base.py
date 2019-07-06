from __future__ import annotations

import importlib
from abc import ABC
import firefly_di as di
import firefly.domain as ffd


class ModuleBase(ABC, ffd.LoggerAware):
    def load_container(self, name: str, bus: ffd.MessageBus):
        try:
            self.debug('Attempting to import module {}.application'.format(name))
            module = importlib.import_module('{}.application'.format(name))
            container_class = getattr(module, 'Container')
            self.debug('Container imported successfully')
        except (ModuleNotFoundError, AttributeError):
            self.debug('Failed to load application module for {}. Ignoring.', name)

            class EmptyContainer(di.Container):
                pass
            container_class = EmptyContainer

        self.debug('Injecting message bus into container')
        container_class.message_bus = bus
        container_class.__annotations__['message_bus'] = ffd.MessageBus
        container = container_class()

        return container
