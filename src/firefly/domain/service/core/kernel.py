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
from pprint import pprint
from typing import Optional, Type, Callable, List, Dict, get_type_hints

import firefly.domain as ffd
import firefly.infrastructure as ffi
import firefly_di as di
import inflection
import firefly.domain.constants as const
import firefly.domain.error as errors

CATEGORIES = ('read', 'write', 'admin')


class Kernel(di.Container, ffd.SystemBusAware, ffd.LoggerAware):
    _service_cache: dict = {}
    _app = None
    _entities: List[Type[ffd.Entity]] = []
    _application_services: List[Type[ffd.ApplicationService]] = []
    _http_endpoints: List[dict] = []
    _event_listeners: Dict[str, List[ffd.ApplicationService]] = {}
    _command_handlers: Dict[str, ffd.ApplicationService] = {}
    _query_handlers: Dict[str, ffd.ApplicationService] = {}
    _timers: list = []

    def __init__(self):
        super().__init__()

        self.__class__.__annotations__ = {}

        logging.info('Bootstrapping container with essential services.')
        self._bootstrap_container()

    def boot(self) -> Kernel:
        self._load_layer('firefly', 'domain', {}, self._add_domain_object)

        for k, v in self.configuration.contexts.items():
            if k == 'firefly' or (v or {}).get('is_extension', 'False') is False:
                continue
            self._load_context(k, v or {})

        for k, v in self.configuration.contexts.items():
            if k == 'firefly' or (v or {}).get('is_extension', 'False') is True:
                continue
            self._load_context(k, v or {})

        self._build_application_services()

        for k, v in get_type_hints(self.__class__).items():
            if inspect.isclass(v) and issubclass(v, ffd.Application):
                self._app = getattr(self, k)
                break

        if self._app is None:
            raise errors.ConfigurationError(
                "No application has been registered with the container. Have you installed a service extension such "
                "as firefly-aws?"
            )
        self._app.initialize(self)

        return self

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

    def _bootstrap_container(self):
        self._register_object('logger', ffi.PythonLogger)
        self._register_object('configuration_factory', ffi.YamlConfigurationFactory)
        self._register_object('configuration', ffd.Configuration, lambda s: s.configuration_factory())

    def _register_object(self, name: str, type_: Type, constructor: Optional[Callable] = None):
        setattr(self.__class__, name, constructor) if constructor is not None else setattr(self.__class__, name, type_)
        self.__class__.__annotations__[name] = type_

    def _build_application_services(self):
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
                self._event_listeners[self._build_service(cls)] = getattr(cls, const.EVENTS)

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

    def _build_service(self, cls):
        if cls not in self._service_cache:
            self._service_cache[cls] = self.build(cls)
        return self._service_cache[cls]

    def _load_context(self, context_name: str, config: dict):
        self._load_layer(context_name, 'domain', config, self._add_domain_object)
        self._load_layer(context_name, 'infrastructure', config, self._add_domain_object)
        self._load_layer(context_name, 'application', config, self._add_application_object)
        self._load_layer(context_name, 'presentation', config, self._add_presentation_object)

    def _load_layer(self, context_name, layer_name: str, config: dict, cb: Callable):
        module_name = config.get('entity_module', '{}.' + layer_name).format(context_name)
        try:
            module = importlib.import_module(module_name)
        except (ModuleNotFoundError, KeyError):
            return

        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            cb(k, v)

    def _add_domain_object(self, k: str, v: type):
        if issubclass(v, ffd.Entity):
            v._logger = self.logger
            self._entities.append(v)
        elif issubclass(v, ffd.ValueObject):
            v._logger = self._logger
        elif self._should_autowire(v):
            self._register_object(inflection.underscore(k), v)

    def _add_infrastructure_object(self, k: str, v: type):
        if self._should_autowire(v):
            self._register_object(inflection.underscore(k), v)

    def _add_application_object(self, k: str, v: type):
        if issubclass(v, ffd.ApplicationService):
            if v not in self._application_services:
                self._application_services.append(v)
        elif self._should_autowire(v):
            self._register_object(inflection.underscore(k), v)

    def _add_presentation_object(self, k: str, v: type):
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
