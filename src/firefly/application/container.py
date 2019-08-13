from __future__ import annotations

import firefly_di as di

import firefly.domain as ffd
import firefly.infrastructure as ffi


class Container(di.Container):
    event_buffer: ffd.EventBuffer = ffd.EventBuffer
    logger: ffd.Logger = ffi.PythonLogger
    serializer: ffd.Serializer = ffi.DefaultSerializer
    configuration: ffd.Configuration = ffi.YamlConfiguration
    command_bus: ffd.CommandBus = lambda self: self.build(ffd.CommandBus, middleware=[
        self.build(ffd.LoggingMiddleware)
    ])
    event_bus: ffd.EventBus = lambda self: self.build(ffd.EventBus, middleware=[
        self.build(ffd.LoggingMiddleware)
    ])
    query_bus: ffd.QueryBus = lambda self: self.build(ffd.QueryBus, middleware=[
        self.build(ffd.LoggingMiddleware)
    ])
    system_bus: ffd.SystemBus = ffd.SystemBus
    context_map: ffd.ContextMap = ffd.ContextMap
    registry: ffd.Registry = ffd.Registry
    message_factory: ffd.MessageFactory = ffd.MessageFactory

    # Infrastructure
    cli_device: ffi.CliDevice = lambda self: self.build(ffi.CliDevice, device_id='firefly')
    http_device: ffi.HttpDevice = ffi.HttpDevice
