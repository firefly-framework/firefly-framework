from __future__ import annotations

import importlib
import inspect
from typing import Callable

import firefly.domain as ffd
import firefly_di as di

from ..logging.logger import LoggerAware
from ..messaging.message_bus import MessageBusAware


class Extension(LoggerAware, MessageBusAware):
    def __init__(self, name: str, logger: ffd.Logger, config: dict, bus: ffd.MessageBus,
                 container: di.Container = None):
        self.name = name
        self._logger = logger
        self._config = config
        self._bus = bus
        self._listeners = []
        self._handlers = []
        self._services = []
        self._service_instances = {}
        self.container = container

        self._bus.insert(1, self._handle_message)

        if self.container is None:
            self._load_container()
        self._load_framework_event_listeners_and_handlers()

    def initialize(self):
        self._load_application_services()
        self._load_api_layer()

    def service_instance(self, cls):
        if cls not in self._service_instances:
            self._service_instances[cls] = self.container.build(cls)

        return self._service_instances[cls]

    def _load_container(self):
        try:
            self.debug('Attempting to import module {}.application', self.name)
            module = importlib.import_module('{}.application'.format(self.name))
            container_class = getattr(module, 'Container')
            self.debug('Container imported successfully')
        except (ModuleNotFoundError, AttributeError):
            self.debug('Failed to load application module for {}. Ignoring.', self.name)

            class EmptyContainer(di.Container):
                pass
            container_class = EmptyContainer

        self.debug('Injecting message bus into container')
        container_class.message_bus = self._bus
        container_class.__annotations__['message_bus'] = ffd.MessageBus
        self.container = container_class()

    def _load_api_layer(self):
        try:
            self.debug('Attempting to import module {}.api', self.name)
            module = importlib.import_module('{}.api'.format(self.name))
        except ModuleNotFoundError:
            self.debug('Failed to load module. Ignoring.')
            return

        for name, cls in module.__dict__.items():
            if hasattr(cls, '__ff_port'):
                self.dispatch(ffd.RegisterPort(target=cls, **getattr(cls, '__ff_port')))
            if hasattr(cls, '__ff_middleware'):
                self.dispatch(ffd.RegisterPresentationMiddleware(self.container.build(cls)))

    def _load_application_services(self):
        try:
            self.debug('Attempting to import module {}.application.service', self.name)
            module = importlib.import_module('{}.application.service'.format(self.name))
        except ModuleNotFoundError:
            self.debug('Failed to load module. Ignoring.')
            return

        for name, cls in module.__dict__.items():
            if inspect.isclass(cls) and issubclass(cls, ffd.Service):
                self._services.append(cls)

    def _load_framework_event_listeners_and_handlers(self):
        try:
            self.debug('Attempting to import module {}.infrastructure.service', self.name)
            module = importlib.import_module('{}.infrastructure.service'.format(self.name))
        except ModuleNotFoundError:
            self.debug('Failed to load module. Ignoring.')
            return

        for name, cls in module.__dict__.items():
            if inspect.isclass(cls) and issubclass(cls, ffd.Service):
                if hasattr(cls, '__ff_listener'):
                    listener = getattr(cls, '__ff_listener')
                    listener['cls'] = cls
                    self._listeners.append(listener)
                if hasattr(cls, '__ff_handler'):
                    handler = getattr(cls, '__ff_handler')
                    handler['cls'] = cls
                    self._handlers.append(handler)

    def _handle_message(self, message: ffd.Message, next_: Callable):
        if isinstance(message, ffd.Event):
            return self._handle_listeners(message, next_)
        if isinstance(message, ffd.Command):
            return self._handle_commands(message, next_)
        if isinstance(message, ffd.Request) and message.service in self._services:
            return next_(self._execute_service(self.service_instance(message.service), message))

        return next_(message)

    def _handle_listeners(self, message: ffd.Message, next_: Callable):
        self.debug('Looking for event listeners')
        if not isinstance(message, ffd.Event):
            return next_(message)

        for listener in self._listeners:
            if (isinstance(listener['event'], str) and listener['event'] == message.__name__) \
                    or isinstance(message, listener['event']):
                self._execute_service(self.service_instance(listener['cls']), message)

        return next_(message)

    def _handle_commands(self, message: ffd.Message, next_: Callable):
        self.debug('Looking for command handler')
        if not isinstance(message, ffd.Command):
            return next_(message)

        for handler in self._handlers:
            if (isinstance(handler['command'], str) and handler['command'] == message.__name__) \
                    or isinstance(message, handler['command']):
                return self._execute_service(self.service_instance(handler['cls']), message)

        return next_(message)

    def _execute_service(self, service: ffd.Service, message: ffd.Message):
        self.debug('Executing {}', service)
        ret = service(body=message.body(), **message.headers())
        if isinstance(ret, ffd.Message):
            return ret

        if ret is not None:
            return ffd.Response(body=ret, headers=message.headers())

        return message
