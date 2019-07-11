from __future__ import annotations

from dataclasses import asdict
from typing import Optional, Union, Callable

import firefly.domain as ffd


@ffd.command_handler(ffd.RegisterCliPort)
class RegisterPort(ffd.Middleware):
    kernel: ffd.Kernel = None

    def __call__(self, message: ffd.Message, next_: Callable):
        self.kernel.register_port(message)

        return True
