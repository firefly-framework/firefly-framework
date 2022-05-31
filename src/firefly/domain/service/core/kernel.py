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
from typing import Optional, Type, Callable, List, Dict, Any

import boto3
from devtools import debug
from dotenv import load_dotenv

import firefly.domain as ffd
import firefly.domain.constants as const
import inflection
import python_jwt
from sqlalchemy import MetaData, event
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.ddl import DDL
from firefly.domain.entity.entity import Base


def bind_metadata(self):
    meta = Base.metadata
    meta.bind = self.sqlalchemy_engine
    return meta


class Kernel(ffd.Container, ffd.SystemBusAware, ffd.LoggerAware):
    _service_cache: dict = {}
    _app: ffd.FastApiApplication = None
    _entities: List[Type[ffd.Entity]] = []
    _aggregates: List[Type[ffd.AggregateRoot]] = []
    _value_objects: List[Type[ffd.ValueObject]] = []
    _application_services: List[Type[ffd.ApplicationService]] = []
    _http_endpoints: List[dict] = []
    _cli_endpoints: List[dict] = []
    _event_listeners: Dict[str, List[ffd.ApplicationService]] = {}
    _command_handlers: Dict[str, ffd.ApplicationService] = {}
    _query_handlers: Dict[str, ffd.ApplicationService] = {}
    _middleware: List[str] = []
    _timers: list = []
    _context: str = None

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
        self._app = self.chalice_application if os.environ.get('DEPLOYMENT_MODE', 'lambda') == 'lambda' else \
            self.fastapi_application
        self._build_services()
        self._app.initialize(self)

        for t in self._value_objects + self._entities:
            t._logger = self.logger
            if issubclass(t, ffd.ValueObject):
                t._session = self.sqlalchemy_session

        event.listen(
            self.sqlalchemy_metadata,
            'before_create',
            DDL(f"CREATE SCHEMA IF NOT EXISTS {self._context}")
        )

        return self

    def process(self, message: ffd.Message) -> Any:
        app_service = None
        if isinstance(message, ffd.Command) and str(message) in self._command_handlers:
            app_service = self._command_handlers[str(message)]
        elif isinstance(message, ffd.Query) and str(message) in self._query_handlers:
            app_service = self._query_handlers[str(message)]
        elif isinstance(message, ffd.Event) and str(message) in self._event_listeners:
            return list(map(
                lambda s: s(**ffd.build_argument_list(message.to_dict(), s)),
                self._event_listeners[str(message)]
            ))

        if app_service is None:
            raise ffd.ConfigurationError()

        return app_service(**ffd.build_argument_list(message.to_dict(), app_service))

    def user_sub(self):
        if os.environ.get('TEST_USER_SUB'):
            return os.environ.get('TEST_USER_SUB')

        headers, claims = self.user_token()
        if headers is not None:
            return headers.get('sub')

    def user_token(self):
        current_request = self.current_request()
        if current_request is None:
            return None, None

        if os.environ.get('TEST_USER_TOKEN_HEADERS') and os.environ.get('TEST_USER_TOKEN_CLAIMS'):
            return self.serializer.deserialize(os.environ.get('TEST_USER_TOKEN_HEADERS')), \
                   self.serializer.deserialize(os.environ.get('TEST_USER_TOKEN_CLAIMS'))

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
        try:
            header, claims = self.user_token()
        except ValueError as e:
            if 'not enough values to unpack' not in str(e):
                raise e
            return False

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

    def register_command(self, cls):
        self._command_handlers[str(getattr(cls, const.COMMAND))] = self._build_service(cls)

    def register_query(self, cls):
        self._query_handlers[str(getattr(cls, const.QUERY))] = self._build_service(cls)

    def current_request(self):
        return self.get_application().app.current_request

    def _initialize_entity_crud_operations(self):
        for entity in self._entities:
            entity._session = self.sqlalchemy_session
            for endpoint in getattr(entity, const.HTTP_ENDPOINTS, []):
                service = self._locate_service_for_entity(entity, endpoint.method)
                if len(list(filter(
                        lambda s: s['route'] == endpoint.route and s['method'] == endpoint.method, self._http_endpoints
                ))) == 0:
                    self._http_endpoints.append({
                        'service': service,
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
        import firefly.infrastructure as ffi

        self.register_object('logger', ffi.DefaultLogger)
        self.register_object('system_bus', ffd.SystemBus)
        self.register_object('cognito_factory', ffd.CognitoFactory, lambda s: s.build(ffi.DefaultCognitoFactory))
        self.register_object('routes_rest_router', ffi.RoutesRestRouter)
        self.register_object('configuration_factory', ffi.YamlConfigurationFactory)
        self.register_object('message_factory', ffd.MessageFactory)
        self.register_object('serializer', ffd.Serializer)
        self.register_object('configuration', ffd.Configuration, lambda s: s.configuration_factory())
        self.register_object('fastapi_application', ffd.FastApiApplication)
        self.register_object('chalice_application', ffd.ChaliceApplication)
        self.register_object('registry', ffd.Registry)
        self.register_object('argparse_executor', ffi.ArgparseExecutor)
        self.register_object('resource_name_generator', ffd.ResourceNameGenerator)
        self.register_object('agent', ffd.Agent, lambda s: s.build(ffi.AwsAgent))

        self.register_object('sqlalchemy_engine_factory', ffi.EngineFactory)
        self.register_object('sqlalchemy_engine', Engine, lambda s: s.sqlalchemy_engine_factory(True))
        self.register_object('sqlalchemy_connection', Connection, lambda s: s.sqlalchemy_engine.connect())
        self.register_object(
            'sqlalchemy_sessionmaker', sessionmaker, lambda s: sessionmaker(bind=s.sqlalchemy_connection)
        )
        self.register_object('sqlalchemy_session', Session, lambda s: s.sqlalchemy_sessionmaker())
        self.register_object('sqlalchemy_metadata', MetaData, bind_metadata)
        self.register_object(
            'repository_factory', ffd.RepositoryFactory, lambda s: s.build(ffi.SqlalchemyRepositoryFactory)
        )
        self.register_object('convert_criteria_to_sqlalchemy', ffd.ConvertCriteriaToSqlalchemy)

        self.register_object('cloudformation_client', constructor=lambda s: boto3.client('cloudformation'))
        self.register_object('ddb_client', constructor=lambda s: boto3.client('dynamodb'))
        self.register_object('lambda_client', constructor=lambda s: boto3.client('lambda'))
        self.register_object('sns_client', constructor=lambda s: boto3.client('sns'))
        self.register_object('sqs_client', constructor=lambda s: boto3.client('sqs'))
        self.register_object('s3_client', constructor=lambda s: boto3.client('s3'))
        self.register_object('kinesis_client', constructor=lambda s: boto3.client('kinesis'))
        self.register_object('cognito_client', constructor=lambda s: boto3.client('cognito-idp'))

    def _build_services(self):
        middleware = []
        for cls in self._middleware:
            middleware.append(getattr(self, cls))
        self._middleware = middleware

        for cls in self._application_services:
            if hasattr(cls, const.HTTP_ENDPOINTS):
                for endpoint in getattr(cls, const.HTTP_ENDPOINTS):
                    self._http_endpoints.append({
                        'service': self._build_service(cls),
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
                        'command': timer.command,
                        'environment': timer.environment,
                        'cron': timer.cron,
                    })

    def _build_service(self, cls):
        if cls not in self._service_cache:
            try:
                self._service_cache[cls] = self.build(cls)
            except OperationalError:
                self._service_cache[cls] = None
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
        if v is Kernel:
            return

        if issubclass(v, ffd.Entity) and v is not ffd.Entity and context != 'firefly':
            if context == self._context and v not in self._entities:
                self._entities.append(v)
                if issubclass(v, ffd.AggregateRoot) and v is not ffd.AggregateRoot:
                    self._aggregates.append(v)
        elif issubclass(v, ffd.ValueObject):
            self._value_objects.append(v)
        elif self._should_autowire(v):
            self.register_object(inflection.underscore(k), v)

    def _add_infrastructure_object(self, k: str, v: type, context: str):
        key = inflection.underscore(k)
        self.register_object(key, v)
        if issubclass(v, ffd.Middleware) and getattr(v, const.MIDDLEWARE, None) is not None:
            self._middleware.append(key)

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
