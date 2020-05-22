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

import firefly.application as ffa
import firefly.domain as ffd
import firefly.infrastructure as ffi
import firefly_di as di
from jinja2 import Environment, PackageLoader


class Container(di.Container):
    kernel: ffd.Kernel = ffd.Kernel
    event_buffer: ffd.EventBuffer = ffd.EventBuffer
    logger: ffd.Logger = ffi.PythonLogger
    serializer: ffd.Serializer = ffi.DefaultSerializer
    configuration_factory: ffd.ConfigurationFactory = ffi.YamlConfigurationFactory
    configuration: ffd.Configuration = lambda self: self.configuration_factory()
    context_map: ffd.ContextMap = ffd.ContextMap
    registry: ffd.Registry = ffd.Registry
    message_factory: ffd.MessageFactory = ffd.MessageFactory
    validator: ffd.Validation = ffd.Validation

    # System Bus
    event_resolver: ffd.EventResolvingMiddleware = lambda self: self.build(
        ffd.EventResolvingMiddleware, event_listeners={
            ffd.ContainersLoaded: [
                ffa.LoadInfrastructureLayer,
                ffa.LoadEntities,
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
    })
    command_bus: ffd.CommandBus = lambda self: self.build(ffd.CommandBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.content_negotiator,
        self.build(ffd.EventDispatchingMiddleware),
        self.command_resolver,
    ])
    event_bus: ffd.EventBus = lambda self: self.build(ffd.EventBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.event_resolver,
    ])
    query_bus: ffd.QueryBus = lambda self: self.build(ffd.QueryBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.content_negotiator,
        self.query_resolver,
    ])
    system_bus: ffd.SystemBus = ffd.SystemBus

    # Storage
    db_api_storage_interface_registry: ffi.DbApiStorageInterfaceRegistry = ffi.DbApiStorageInterfaceRegistry

    # API
    web_server: ffi.WebServer = ffi.WebServer
    cli_executor: ffd.CliAppExecutor = ffi.ArgparseExecutor
    rest_router: ffd.RestRouter = ffi.RoutesRestRouter

    # Deployment
    agent_factory: ffd.AgentFactory = lambda self: self.build(ffd.AgentFactory, agents={
        'default': self.build(ffi.DefaultAgent)
    })
