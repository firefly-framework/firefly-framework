#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

import importlib
import inspect
import logging
from typing import Optional, Type, Callable, List, Dict

import boto3
import firefly.domain as ffd
import firefly.domain.constants as const
import firefly.infrastructure as ffi
import inflection
from firefly.application.container import Container
from firefly.infrastructure.service.core.chalice_application import ChaliceApplication
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import sessionmaker, Session

# CATEGORIES = ('read', 'write', 'admin')


class Kernel(Container, ffd.SystemBusAware, ffd.LoggerAware):
    _service_cache: dict = {}
    _app: ChaliceApplication = None
    _entities: List[Type[ffd.Entity]] = []
    _aggregates: List[Type[ffd.AggregateRoot]] = []
    _application_services: List[Type[ffd.ApplicationService]] = []
    _http_endpoints: List[dict] = []
    _event_listeners: Dict[str, List[ffd.ApplicationService]] = {}
    _command_handlers: Dict[str, ffd.ApplicationService] = {}
    _query_handlers: Dict[str, ffd.ApplicationService] = {}
    _middleware: List[Type[ffd.Middleware]] = []
    _timers: list = []

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        super().__init__()

        self.__class__.__annotations__ = {}

        logging.info('Bootstrapping container with essential services.')
        self._bootstrap_container()

    def boot(self) -> Kernel:
        for layer in ('domain', 'infrastructure', 'application', 'presentation'):
            self._load_layer('firefly', layer, {}, getattr(self, f'_add_{layer}_object'))

        for k, v in self.configuration.contexts.items():
            if k == 'firefly' or (v or {}).get('is_extension', 'False') is False:
                continue
            self._load_context(k, v or {})

        for k, v in self.configuration.contexts.items():
            if k == 'firefly' or (v or {}).get('is_extension', 'False') is True:
                continue
            self._load_context(k, v or {})

        self._app = self.chalice_application
        self._build_services()
        self._app.initialize(self)
        self.initialize_storage()

        return self

    def get_application(self) -> ffd.Application:
        return self._app

    def get_http_endpoints(self):
        return self._http_endpoints

    def get_command_handlers(self):
        return self._command_handlers

    def get_event_listeners(self):
        return self._event_listeners

    def get_query_handlers(self):
        return self._query_handlers

    def get_timers(self):
        return self._timers

    def get_entities(self):
        return self._entities

    def get_aggregates(self):
        return self._aggregates

    def get_middleware(self):
        return self._middleware

    def register_object(self, name: str, type_: Type = type, constructor: Optional[Callable] = None):
        if hasattr(self.__class__, name):
            return
        setattr(self.__class__, name, constructor) if constructor is not None else setattr(self.__class__, name, type_)
        self.__class__.__annotations__[name] = type_

    def _bootstrap_container(self):
        self.register_object('logger', ffi.ChaliceLogger)
        self.register_object('configuration_factory', ffi.YamlConfigurationFactory)
        self.register_object('message_transport', ffd.MessageTransport, lambda s: s.build(ffi.ChaliceMessageTransport))
        self.register_object('message_factory', ffd.MessageFactory)
        self.register_object('system_bus', ffd.SystemBus)
        self.register_object('serializer', ffd.Serializer)
        self.register_object('map_entities', ffd.MapEntities)
        self.register_object('parse_relationships', ffd.ParseRelationships)
        self.register_object('configuration', ffd.Configuration, lambda s: s.configuration_factory())
        self.register_object('chalice_application', ChaliceApplication)

        self.register_object('sqlalchemy_engine_factory', ffi.EngineFactory)
        self.register_object('sqlalchemy_engine', Engine, lambda s: s.sqlalchemy_engine_factory(True))
        self.register_object('sqlalchemy_connection', Connection, lambda s: s.sqlalchemy_engine.connect())
        self.register_object('sqlalchemy_sessionmaker', sessionmaker, lambda s: sessionmaker(bind=s.sqlalchemy_engine))
        self.register_object('sqlalchemy_session', Session, lambda s: s.sqlalchemy_sessionmaker())
        self.register_object('sqlalchemy_metadata', MetaData, lambda s: MetaData(bind=s.sqlalchemy_engine))
        self.register_object(
            'repository_factory', ffd.RepositoryFactory, lambda s: s.build(ffi.SqlalchemyRepositoryFactory)
        )

        self.register_object('cloudformation_client', constructor=lambda s: boto3.client('cloudformation'))
        self.register_object('ddb_client', constructor=lambda s: boto3.client('dynamodb'))
        self.register_object('lambda_client', constructor=lambda s: boto3.client('lambda'))
        self.register_object('sns_client', constructor=lambda s: boto3.client('sns'))
        self.register_object('sqs_client', constructor=lambda s: boto3.client('sqs'))
        self.register_object('s3_client', constructor=lambda s: boto3.client('s3'))
        self.register_object('kinesis_client', constructor=lambda s: boto3.client('kinesis'))

    def _build_services(self):
        for cls in self._application_services:
            if hasattr(cls, const.HTTP_ENDPOINTS):
                for endpoint in getattr(cls, const.HTTP_ENDPOINTS):
                    self._http_endpoints.append({
                        'service': self.build(cls),
                        'gateway': endpoint.gateway,
                        'route': endpoint.route,
                        'method': endpoint.method,
                        'query_params': endpoint.query_params,
                        'secured': endpoint.secured,
                        'scopes': endpoint.scopes,
                        'tags': endpoint.tags,
                    })

            if hasattr(cls, const.EVENTS):
                for e in getattr(cls, const.EVENTS):
                    if str(e) not in self._event_listeners:
                        self._event_listeners[str(e)] = []
                    self._event_listeners[str(e)].append(self._build_service(cls))

            if hasattr(cls, const.COMMAND):
                self._command_handlers[str(getattr(cls, const.COMMAND))] = self._build_service(cls)

            if hasattr(cls, const.QUERY):
                self._query_handlers[str(getattr(cls, const.QUERY))] = self._build_service(cls)

            if hasattr(cls, const.TIMERS):
                for timer in getattr(cls, const.TIMERS):
                    self._timers.append({
                        'service': self._build_service(cls),
                        'id': timer.id,
                        'command': timer.command,
                        'environment': timer.environment,
                        'cron': timer.cron,
                    })

        middleware = []
        for cls in self._middleware:
            middleware.append(self._build_service(cls))
        self._middleware = middleware

    def _build_service(self, cls):
        if cls not in self._service_cache:
            self._service_cache[cls] = self.build(cls)
        return self._service_cache[cls]

    def _load_context(self, context_name: str, config: dict):
        self._load_layer(context_name, 'domain', config, self._add_domain_object)
        self._load_layer(context_name, 'infrastructure', config, self._add_infrastructure_object)
        self._load_layer(context_name, 'application', config, self._add_application_object)
        self._load_layer(context_name, 'presentation', config, self._add_presentation_object)

    def _load_layer(self, context_name, layer_name: str, config: dict, cb: Callable):
        module_name = config.get(f'{layer_name}_module', '{}.' + layer_name).format(context_name)
        try:
            module = importlib.import_module(module_name)
        except (ModuleNotFoundError, KeyError):
            return

        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            cb(k, v, context_name)

    def _add_domain_object(self, k: str, v: type, context: str):
        if issubclass(v, ffd.Entity) and v is not ffd.Entity and context != 'firefly':
            v._logger = self.logger
            self._entities.append(v)
            if issubclass(v, ffd.AggregateRoot) and v is not ffd.AggregateRoot:
                self._aggregates.append(v)
        elif issubclass(v, ffd.ValueObject):
            v._logger = self.logger
            v._session = self.sqlalchemy_session
        elif self._should_autowire(v):
            self.register_object(inflection.underscore(k), v)

    def _add_infrastructure_object(self, k: str, v: type, context: str):
        if issubclass(v, ffd.Middleware) and getattr(v, const.MIDDLEWARE, None) is not None:
            self._middleware.append(v)
        elif self._should_autowire(v):
            self.register_object(inflection.underscore(k), v)

    def _add_application_object(self, k: str, v: type, context: str):
        if issubclass(v, ffd.ApplicationService):
            if v not in self._application_services:
                self._application_services.append(v)
        elif self._should_autowire(v):
            self.register_object(inflection.underscore(k), v)

    def _add_presentation_object(self, k: str, v: type, context: str):
        pass

    def _should_autowire(self, v):
        if inspect.isabstract(v) or \
                issubclass(v, Exception):
            return False

        return True

    # @property
    # def is_authorized(self):
    #     self.info('Calling is_authorized')
    #     if self.required_scopes is None or len(self.required_scopes) == 0:
    #         self.info(f'Required scopes: {self.required_scopes}')
    #         if self.required_scopes is not None:
    #             self.info(f'len(self.required_scopes): {len(self.required_scopes)}')
    #         return True  # No required scopes, return True
    #
    #     if self.user is None:
    #         self.info("User is none")
    #         return self.secured is False
    #
    #     if len(self.user.scopes) > 0:
    #         for scope in self.required_scopes:
    #             for user_scope in self.user.scopes:
    #                 self.info(f'{user_scope} in {self.user.scopes}')
    #                 if self._has_grant(scope, user_scope):
    #                     self.info('has grant')
    #                     return True
    #
    #     self.info("not authorized")
    #
    #     return False
    #
    # def is_admin(self, service: str):
    #     if not self.user or not self.user.scopes or len(self.user.scopes) == 0:
    #         return False
    #
    #     for scope in self.user.scopes:
    #         if scope.lower() == f'{service}.admin':
    #             return True
    #
    #     return False
    #
    # @staticmethod
    # def _has_grant(scope: str, user_scope: str):
    #     parts = scope.lower().split('.')
    #     user = user_scope.lower().split('.')
    #
    #     for i, part in enumerate(parts):
    #         if i >= len(user):
    #             return False
    #
    #         if user[i] == 'admin':
    #             return True
    #
    #         if part not in CATEGORIES and part != user[i]:
    #             return False
    #
    #         if part in CATEGORIES:
    #             if user[i] not in CATEGORIES:
    #                 return False
    #             if part == 'admin':
    #                 return False
    #             if part == 'write':
    #                 return user[i] == 'write'
    #             if part == 'read':
    #                 return user[i] in ('read', 'write')
    #
    #     return True
    #
    # def has_tenant(self):
    #     return self.user is not None and self.user.tenant is not None
    #
    # def reject_missing_tenant(self):
    #     if not self.has_tenant():
    #         raise ffd.Unauthorized()
    #
    # def reject_if_missing(self, scopes: Union[str, List[str]]):
    #     if self.user is None:
    #         raise ffd.Unauthorized()
    #
    #     if isinstance(scopes, str):
    #         scopes = [scopes]
    #     for my_scope in self.user.scopes:
    #         reject = True
    #         for scope in scopes:
    #             if self._has_grant(my_scope, scope):
    #                 reject = False
    #                 break
    #         if reject:
    #             raise ffd.Unauthorized()
