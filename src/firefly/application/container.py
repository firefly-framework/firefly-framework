from __future__ import annotations

import firefly_di as di

import firefly.domain as ffd
import firefly.infrastructure as ffi


class Container(di.Container):
    logger: ffd.Logger = ffi.PythonLogger
    configuration: ffd.Configuration = ffi.YamlConfiguration
    message_bus: ffd.MessageBus = lambda self: ffd.MessageBus([
        self.build(ffd.LoggingMiddleware)
    ])
    context_map: ffd.ContextMap = ffd.ContextMap
