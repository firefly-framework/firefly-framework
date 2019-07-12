from __future__ import annotations

from typing import Callable

import firefly.domain as ffd
import firefly.infrastructure as ffi


@ffd.command_handler(ffd.RegisterCliPort)
class RegisterCliPort(ffd.Middleware):
    _cli_device: ffi.CliDevice = None

    def __call__(self, message: ffd.RegisterCliPort, next_: Callable):
        self._cli_device.register_port(message)
