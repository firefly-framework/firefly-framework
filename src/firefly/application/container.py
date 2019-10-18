from __future__ import annotations

import firefly.application as ffa
import firefly.domain as ffd
import firefly.infrastructure as ffi
import firefly_di as di


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

    # System Bus
    event_resolver: ffd.EventResolvingMiddleware = lambda self: self.build(
        ffd.EventResolvingMiddleware, event_listeners={
            ffd.ContainersLoaded: [ffa.LoadApplicationServices],
            ffd.ApplicationServicesLoaded: [
                ffa.LoadEntities,
                ffa.LoadUi
            ],
            ffd.DomainEntitiesLoaded: [ffa.AutoGenerateAggregateApis],
        }
    )
    command_resolver: ffd.CommandResolvingMiddleware = lambda self: self.build(
        ffd.CommandResolvingMiddleware, command_handlers={
            ffd.LoadContainers: ffa.LoadContainers,
        }
    )
    query_resolver: ffd.QueryResolvingMiddleware = ffd.QueryResolvingMiddleware
    command_bus: ffd.CommandBus = lambda self: self.build(ffd.CommandBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.build(ffd.EventDispatchingMiddleware),
        self.command_resolver,
    ])
    event_bus: ffd.EventBus = lambda self: self.build(ffd.EventBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.event_resolver,
    ])
    query_bus: ffd.QueryBus = lambda self: self.build(ffd.QueryBus, middleware=[
        self.build(ffd.LoggingMiddleware),
        self.query_resolver,
    ])
    system_bus: ffd.SystemBus = ffd.SystemBus

    # Web Server
    web_server: ffi.WebServer = ffi.WebServer

    # Deployment
    agent_factory: ffd.AgentFactory = lambda self: self.build(ffd.AgentFactory, agents={
        'default': self.build(ffi.DefaultAgent)
    })
