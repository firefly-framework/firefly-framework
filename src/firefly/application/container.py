from __future__ import annotations

import firefly_di as di

import firefly.domain as ffd
import firefly.infrastructure as ffi


class Container(di.Container):
    event_buffer: ffd.EventBuffer = ffd.EventBuffer
    logger: ffd.Logger = ffi.PythonLogger
    serializer: ffd.Serializer = ffi.DefaultSerializer
    configuration: ffd.Configuration = ffi.YamlConfiguration
    command_bus: ffd.CommandBus = lambda self: ffd.CommandBus([
        self.build(ffd.LoggingMiddleware)
    ])
    event_bus: ffd.EventBus = lambda self: ffd.EventBus([
        self.build(ffd.LoggingMiddleware)
    ])
    query_bus: ffd.QueryBus = lambda self: ffd.QueryBus([
        self.build(ffd.LoggingMiddleware)
    ])
    system_bus: ffd.SystemBus = ffd.SystemBus
    context_map: ffd.ContextMap = ffd.ContextMap

    # Infrastructure
    cli_device: ffi.CliDevice = lambda self: self.build(ffi.CliDevice, device_id='firefly')
    http_device: ffi.HttpDevice = ffi.HttpDevice
