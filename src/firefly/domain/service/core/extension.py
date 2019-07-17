from __future__ import annotations

import importlib
import inspect
from typing import Type, TypeVar

import firefly.domain as ffd
import firefly_di as di

from .service import Service
from ..logging.logger import LoggerAware
from ..messaging.system_bus import SystemBusAware
from ...event.api_loaded import ApiLoaded
from ...event.application_services_loaded import ApplicationServicesLoaded
from ...event.domain_entities_loaded import DomainEntitiesLoaded
from ...event.infrastructure_loaded import InfrastructureLoaded
from ...entity.messaging.event import Event

SERVICE = TypeVar('SERVICE', bound=Service)
EVENT = TypeVar('EVENT', bound=Event)


class Extension(LoggerAware, SystemBusAware):
    MODULES = [
        ('{}.domain.entity', DomainEntitiesLoaded),
        ('{}.api', ApiLoaded),
        ('{}.application.service', ApplicationServicesLoaded),
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
        self._initialize_container()

    def service_instance(self, cls):
        if cls not in self._service_instances:
            try:
                self._service_instances[cls] = self.container.build(cls)
            except TypeError:
                return cls

        return self._service_instances[cls]

    def load_infrastructure(self):
        self._load_module('{}.infrastructure.service', InfrastructureLoaded)

    def _initialize_container(self):
        c = self.container.__class__
        if not hasattr(c, '__annotations__'):
            c.__annotations__ = {}

        c.registry = ffd.Registry
        c.__annotations__['registry'] = ffd.Registry

        self._system_bus.dispatch(ffd.ContainerInitialized(self.name))

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

    def _load_modules(self):
        for module_name, event in self.MODULES:
            self._load_module(module_name, event)

    def _load_module(self, module_name: str, event: Type[EVENT]):
        try:
            self.debug('Attempting to load {}', module_name.format(self.name))
            module = importlib.import_module(module_name.format(self.name))
        except ModuleNotFoundError:
            self.debug('Failed to load module. Ignoring.')
            return

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

        self.dispatch(event(self.name))

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
                self._add_middleware(mw)

        # Implicitly register this Service as a Command/Query handler
        if not registered:
            message = cls.get_message()
            mw = ffd.ServiceExecutingMiddleware(self.service_instance(cls))
            if issubclass(message, ffd.Command):
                setattr(mw, '__ff_command_handler', [{'command': message}])
            else:
                setattr(mw, '__ff_query_handler', [{'query': message}])
            self._add_middleware(mw)

    @staticmethod
    def _wrap_mw(cls: ffd.Middleware, type_=None):
        if type_ is not None:
            return ffd.SubscriptionWrapper(cls, type_)
        return cls
