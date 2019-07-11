from __future__ import annotations

import importlib
import inspect
from typing import Type, TypeVar

import firefly.domain as ffd
import firefly_di as di

from ..logging.logger import LoggerAware
from ..messaging.system_bus import SystemBusAware
from .service import Service

SERVICE = TypeVar('SERVICE', bound=Service)


class Extension(LoggerAware, SystemBusAware):
    MODULES = [
        '{}.infrastructure.service',
        '{}.domain.entity',
        '{}.api',
        '{}.application.service',
    ]

    def __init__(self, name: str, logger: ffd.Logger, config: dict, bus: ffd.SystemBus,
                 container: di.Container = None):
        self.name = name
        self._logger = logger
        self.config = config
        self._system_bus = bus
        self._service_instances = {}
        self.container = container

        if self.container is None:
            self._load_container()

    def initialize(self):
        self._load_modules()
        self.dispatch(ffd.InitializationComplete(self.name))

    def service_instance(self, cls):
        if cls not in self._service_instances:
            try:
                self._service_instances[cls] = self.container.build(cls)
            except TypeError:
                return cls

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
            container_class.__annotations__ = {}

        self.container = container_class()
        self._system_bus.dispatch(ffd.ContainerRegistered(self.name))

    def _load_modules(self):
        for module_name in self.MODULES:
            try:
                self.debug('Attempting to load {}', module_name.format(self.name))
                module = importlib.import_module(module_name.format(self.name))
            except ModuleNotFoundError:
                self.debug('Failed to load module. Ignoring.')
                continue

            for name, cls in module.__dict__.items():
                if not inspect.isclass(cls):
                    continue

                if hasattr(cls, '__ff_port'):
                    self._invoke_port_commands(cls)

                if issubclass(cls, ffd.Middleware):
                    self._add_middleware(cls)
                elif issubclass(cls, ffd.Service):
                    self._add_service(cls)
                elif issubclass(cls, ffd.Entity):
                    cls.event_buffer = self.container.event_buffer

    def _invoke_port_commands(self, cls):
        for data in getattr(cls, '__ff_port'):
            self.invoke(data['command'])
            for k, v in cls.__dict__.items():
                if hasattr(v, '__ff_port'):
                    self._invoke_port_commands(v)

    def _add_middleware(self, cls):
        for key, method, port_key in (('__ff_command_handler', 'add_command_handler', 'command'),
                                      ('__ff_listener', 'add_event_listener', 'event'),
                                      ('__ff_query_handler', 'add_query_handler', 'query')):
            if hasattr(cls, key):
                for handler in getattr(cls, key):
                    getattr(self._system_bus, method)(self._wrap_mw(self.service_instance(cls), handler[port_key]))

    def _add_service(self, cls: Type[SERVICE]):
        registered = False
        for key in ('__ff_command_handler', '__ff_listener', '__ff_query_handler'):
            if hasattr(cls, key):
                registered = True
                mw = ffd.ServiceExecutingMiddleware(self.service_instance(cls))
                setattr(mw, key, getattr(cls, key))
                self._add_middleware(cls)

        # Implicitly register this Service as a Command/Query handler
        if not registered:
            message = cls.get_message()
            mw = ffd.ServiceExecutingMiddleware(self.service_instance(cls))
            if isinstance(message, ffd.Command):
                setattr(mw, '__ff_command_handler', [{'command': message}])
            else:
                setattr(mw, '__ff_query_handler', [{'query': message}])
            self._add_middleware(mw)

    @staticmethod
    def _wrap_mw(cls: ffd.Middleware, type_=None):
        if type_ is not None:
            return ffd.SubscriptionWrapper(cls, type_)
        return cls
