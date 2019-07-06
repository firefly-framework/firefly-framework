from __future__ import annotations

import importlib
from typing import Callable, Dict

import firefly.domain as ffd
import firefly_di as di

from ..logging.logger import LoggerAware


class ContextMap(LoggerAware):
    _config: ffd.Configuration = None
    _firefly_container: di.Container = None

    def __init__(self, bus: ffd.MessageBus):
        self._contexts: Dict[str, ffd.Context] = {}
        self._extensions: Dict[str, ffd.Extension] = {}
        self._bus = bus
        self._bus.add(ffd.LoggingMiddleware('Message is in context map: {}'))
        self._bus.add(self._handle_framework_commands)

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
            extension.initialize()
        for context in self._contexts.values():
            context.initialize()

    def _load_container(self, context_name: str, config: dict):
        try:
            module = importlib.import_module(f'{context_name}.application')
            container_class = getattr(module, 'Container')
            container = container_class()
            container.register_container(self._firefly_container)
        except (ModuleNotFoundError, AttributeError):
            self.debug('Failed to load application module for {}. Ignoring.', context_name)

    def _load_extensions(self):
        self._extensions['firefly'] = ffd.Extension('firefly', self._logger, self._config.all.get('firefly', {}),
                                                    self._bus, self._firefly_container)
        for name, config in self._config.extensions.items():
            if name == 'firefly':
                continue
            self._extensions[name] = ffd.Extension(name, self._logger, config, self._bus)

    def _load_contexts(self):
        for name, config in self._config.contexts.items():
            self._contexts[name] = ffd.Context(name, self._logger, config, self._bus)

    def _handle_framework_commands(self, message: ffd.Message, next_: Callable):
        if isinstance(message, ffd.FrameworkCommand):
            return self._handle(message)
        return next_(message)

    def _handle(self, command: ffd.FrameworkCommand):
        if isinstance(command, ffd.RegisterContainer):
            self.debug('Registering firefly container for context {}'.format(command.body()))
            self._contexts[command.body()].container.register_container(self._firefly_container)
            for name, config in self._contexts[command.body()].extensions.items():
                self.debug('Registering {} extension container for context {}'.format(name, command.body()))
                self._contexts[command.body()].container.register_container(self._extensions[name].container)
            return True

    def _pass_message_to_kernel(self, message: ffd.Message, next_: Callable):
        ret = next_(message)
        self._kernel_bus.dispatch(ret)
        return ret

    def _get_message_from_kernel(self, message: ffd.Message, next_: Callable):
        return next_(self._bus.dispatch(message))
