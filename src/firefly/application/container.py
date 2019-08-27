from __future__ import annotations

import firefly_di as di

import firefly.domain as ffd
import firefly.infrastructure as ffi


class Container(di.Container):
    event_buffer: ffd.EventBuffer = ffd.EventBuffer
    logger: ffd.Logger = ffi.PythonLogger
    serializer: ffd.Serializer = ffi.DefaultSerializer
    configuration: ffd.Configuration = ffi.YamlConfiguration
    context_map: ffd.ContextMap = ffd.ContextMap
    registry: ffd.Registry = ffd.Registry
    message_factory: ffd.MessageFactory = ffd.MessageFactory

    # System Bus
    event_resolver: ffd.EventResolvingMiddleware = lambda self: self.build(
        ffd.EventResolvingMiddleware, event_listeners={
            self.build(ffd.AutoGenerateAggregateApis): 'firefly.DomainEntitiesLoaded',
        }
    )
    command_resolver: ffd.CommandResolvingMiddleware = ffd.CommandResolvingMiddleware
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
