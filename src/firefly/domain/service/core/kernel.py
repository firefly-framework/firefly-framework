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
import os
from pprint import pprint
from typing import Optional, Type, Callable, List, Dict

import boto3
import firefly.domain as ffd
import firefly.domain.constants as const
import firefly.infrastructure as ffi
import inflection
import python_jwt
from chalice.app import Request
from firefly.infrastructure.service.container import Container
from firefly.infrastructure.service.core.chalice_application import ChaliceApplication
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import sessionmaker, Session


class Kernel(Container, ffd.SystemBusAware, ffd.LoggerAware):
    _service_cache: dict = {}
    _app: ChaliceApplication = None
    _entities: List[Type[ffd.Entity]] = []
    _aggregates: List[Type[ffd.AggregateRoot]] = []
    _application_services: List[Type[ffd.ApplicationService]] = []
    _http_endpoints: List[dict] = []
    _cli_endpoints: List[dict] = []
    _event_listeners: Dict[str, List[ffd.ApplicationService]] = {}
    _command_handlers: Dict[str, ffd.ApplicationService] = {}
    _query_handlers: Dict[str, ffd.ApplicationService] = {}
    _middleware: List[Type[ffd.Middleware]] = []
    _timers: list = []
    _context: str = None

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Kernel, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        super().__init__()

        self.__class__.__annotations__ = {}
        self._context = os.environ.get('CONTEXT')

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

        self.auto_generate_aggregate_apis()
        self._initialize_entity_crud_operations()
        self._app = self.chalice_application
        self._build_services()
        self._app.initialize(self)
        self.initialize_storage()

        return self

    def user_token(self):
        current_request: Request = self.current_request()
        token = None
        for k, v in current_request.headers.items():
            if k.lower() == 'authorization':
                token = v.split(' ').pop()
                break

        if token is None:
            return None, None

        # Note that this is NOT verifying the token. It's only reading the headers and claims.
        return python_jwt.process_jwt(token)

    def requesting_user_has_scope(self, scope: str):
        header, claims = self.user_token()
        if claims is None:
            return False

        for s in claims['scope'].split(' '):
            if s == scope:
                return True

        return False

    def get_application(self) -> ffd.Application:
        return self._app

    def get_http_endpoints(self):
        return self._http_endpoints

    def get_cli_endpoints(self):
        return self._cli_endpoints

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
        if type_ is not type:
            self.__class__.__annotations__[name] = type_

    def register_command(self, cls):
        self._command_handlers[str(getattr(cls, const.COMMAND))] = self._build_service(cls)

    def register_query(self, cls):
        self._query_handlers[str(getattr(cls, const.QUERY))] = self._build_service(cls)

    def current_request(self):
        return self.get_application().app.current_request

    def _initialize_entity_crud_operations(self):
        for entity in self._entities:
            for endpoint in getattr(entity, const.HTTP_ENDPOINTS, []):
                service = self._locate_service_for_entity(entity, endpoint.method)
                if len(list(filter(
                        lambda s: s['route'] == endpoint.route and s['method'] == endpoint.method, self._http_endpoints
                ))) == 0:
                    self._http_endpoints.append({
                        'service': service,
                        'gateway': endpoint.gateway,
                        'route': endpoint.route,
                        'method': endpoint.method,
                        'query_params': endpoint.query_params,
                        'secured': endpoint.secured,
                        'scopes': endpoint.scopes,
                        'tags': endpoint.tags,
                    })

    def _locate_service_for_entity(self, entity, method: str):
        t = ''
        key = ''
        try:
            if method.lower() in ('post', 'put', 'delete'):
                prefix = {'post': 'Create', 'put': 'Update', 'delete': 'Delete'}[method.lower()]
                t = 'command'
                key = f'{self._context}.{prefix}{entity.__name__}'
                return self._command_handlers[key]
            else:
                t = 'query'
                key = f'{self._context}.{inflection.pluralize(entity.__name__)}'
                return self._query_handlers[key]
        except KeyError:
            raise ffd.ConfigurationError(f'No {t} handler was generated for {key}')

    def _bootstrap_container(self):
        self.register_object('logger', ffi.ChaliceLogger)
        self.register_object('system_bus', ffd.SystemBus)
        self.register_object('configuration_factory', ffi.YamlConfigurationFactory)
        self.register_object('message_transport', ffd.MessageTransport, lambda s: s.build(ffi.ChaliceMessageTransport))
        self.register_object('message_factory', ffd.MessageFactory)
        self.register_object('serializer', ffd.Serializer)
        self.register_object('map_entities', ffd.MapEntities)
        self.register_object('parse_relationships', ffd.ParseRelationships)
        self.register_object('configuration', ffd.Configuration, lambda s: s.configuration_factory())
        self.register_object('chalice_application', ChaliceApplication)
        self.register_object('registry', ffd.Registry)

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
                        'service': self._build_service(cls),
                        'gateway': endpoint.gateway,
                        'route': endpoint.route,
                        'method': endpoint.method,
                        'query_params': endpoint.query_params,
                        'secured': endpoint.secured,
                        'scopes': endpoint.scopes,
                        'tags': endpoint.tags,
                    })

            if hasattr(cls, const.CLI_ENDPOINTS):
                for endpoint in getattr(cls, const.CLI_ENDPOINTS):
                    self._cli_endpoints.append(endpoint)

            if hasattr(cls, const.EVENTS):
                for e in getattr(cls, const.EVENTS):
                    if str(e) not in self._event_listeners:
                        self._event_listeners[str(e)] = []
                    self._event_listeners[str(e)].append(self._build_service(cls))

            if hasattr(cls, const.COMMAND):
                self.register_command(cls)

            if hasattr(cls, const.QUERY):
                self.register_query(cls)

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
