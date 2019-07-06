from __future__ import annotations

from typing import Optional, Union

import firefly.domain as ffd


@ffd.handle(ffd.RegisterPort)
class RegisterPort(ffd.Service):
    kernel: ffd.Kernel = None

    def __call__(self, body: dict, **kwargs) -> Optional[Union[ffd.Message, object]]:
        del body['__class__']
        self.kernel.register_port(**body)

        return True
