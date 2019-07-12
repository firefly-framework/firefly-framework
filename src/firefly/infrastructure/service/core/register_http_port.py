from __future__ import annotations

from typing import Callable

import firefly.domain as ffd
import firefly.infrastructure as ffi


@ffd.command_handler(ffd.RegisterHttpPort)
class RegisterHttpPort(ffd.Middleware):
    _http_device: ffi.HttpDevice = None

    def __call__(self, message: ffd.RegisterHttpPort, next_: Callable):
        self._http_device.register_port(message)
