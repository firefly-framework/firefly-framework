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

import os

import firefly.application as ffa
import firefly.domain as ffd
import firefly.infrastructure as ffi
import firefly.infrastructure.repository.rdb_storage_interfaces as rsi
import firefly_di as di
from firefly.infrastructure.jinja2 import is_attribute, is_criteria, is_uuid
from jinja2 import Environment, FileSystemLoader
from jinjasql import JinjaSql


def build_jinja(self):
    env = self.jinjasql_environment
    env.tests['attribute'] = is_attribute
    env.tests['criteria'] = is_criteria
    env.tests['uuid'] = is_uuid

    def serialized(entity):
        return self.serializer.serialize(entity)
    env.filters['serialized'] = serialized

    return JinjaSql(env=env, param_style='named')


class Container(di.Container):
    kernel: ffd.Kernel = ffd.Kernel
    event_buffer: ffd.EventBuffer = ffd.EventBuffer
    logger: ffd.Logger = ffi.PythonLogger
    serializer: ffd.Serializer = ffi.JsonSerializer
    json_serializer: ffi.JsonSerializer = ffi.JsonSerializer
    configuration_factory: ffd.ConfigurationFactory = ffi.YamlConfigurationFactory
    configuration: ffd.Configuration = lambda self: self.configuration_factory()
    context_map: ffd.ContextMap = ffd.ContextMap
    registry: ffd.Registry = ffd.Registry
    message_factory: ffd.MessageFactory = ffd.MessageFactory
    validator: ffd.Validator = ffd.Validator

    # System Bus
    event_resolver: ffd.EventResolvingMiddleware = lambda self: self.build(
        ffd.EventResolvingMiddleware, event_listeners={
            ffd.ContainersLoaded: [
                ffa.LoadInfrastructureLayer,
                ffa.LoadDomainLayer,
            ],
            ffd.DomainEntitiesLoaded: [
                ffa.LoadApplicationLayer,
                ffa.AutoGenerateAggregateApis,
            ],
            ffd.ApplicationLayerLoaded: [
                ffa.LoadPresentationLayer,
            ]
        }
    )
    command_resolver: ffd.CommandResolvingMiddleware = lambda self: self.build(
        ffd.CommandResolvingMiddleware, command_handlers={
            ffd.LoadContainers: ffa.LoadContainers,
        }
    )
    query_resolver: ffd.QueryResolvingMiddleware = ffd.QueryResolvingMiddleware
    content_negotiator: ffd.ContentNegotiator = lambda self: ffd.ContentNegotiator({
        'text/html': self.build(ffi.HtmlConverter),
    }, self.logger)
    authenticator: ffa.AuthenticatingMiddleware = ffa.AuthenticatingMiddleware
    authorizer: ffa.AuthorizingMiddleware = ffa.AuthorizingMiddleware
    transaction_handler: ffd.TransactionHandlingMiddleware = ffd.TransactionHandlingMiddleware
    command_bus: ffd.CommandBus = lambda self: self.build(ffd.CommandBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.authenticator,
        self.authorizer,
        self.content_negotiator,
        self.transaction_handler,
        self.build(ffd.EventDispatchingMiddleware),
        self.command_resolver,
    ])
    event_bus: ffd.EventBus = lambda self: self.build(ffd.EventBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.authenticator,
        self.authorizer,
        self.transaction_handler,
        self.event_resolver,
    ])
    query_bus: ffd.QueryBus = lambda self: self.build(ffd.QueryBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.authenticator,
        self.authorizer,
        self.content_negotiator,
        self.transaction_handler,
        self.query_resolver,
    ])
    system_bus: ffd.SystemBus = ffd.SystemBus

    # Storage
    rdb_storage_interface_registry: ffi.RdbStorageInterfaceRegistry = ffi.RdbStorageInterfaceRegistry

    # Messaging
    message_transport: ffd.MessageTransport = ffi.AsyncioMessageTransport

    # API
    web_server: ffi.WebServer = ffi.WebServer
    cli_executor: ffd.CliAppExecutor = ffi.ArgparseExecutor
    rest_router: ffd.RestRouter = ffi.RoutesRestRouter

    # Deployment
    agent_factory: ffd.AgentFactory = lambda self: self.build(ffd.AgentFactory, agents={
        'default': self.build(ffi.DefaultAgent)
    })

    # Templating
    jinjasql_environment: Environment = lambda self: Environment(
        loader=FileSystemLoader([f'{os.path.abspath(os.path.dirname(rsi.__file__))}/templates']),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    jinjasql: JinjaSql = lambda self: build_jinja(self)
