from __future__ import annotations

from typing import Optional, Union, Callable

import firefly.domain as ffd


@ffd.command_handler(ffd.RegisterPort)
class RegisterPort(ffd.Middleware):
    kernel: ffd.Kernel = None

    def __call__(self, message: ffd.Message, next_: Callable):
        body = message.body()
        del body['__class__']
        self.kernel.register_port(**body)

        return True
