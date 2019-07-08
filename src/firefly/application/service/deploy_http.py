from __future__ import annotations

from typing import Optional, Union

import firefly.domain as ffd
import firefly.infrastructure as ffi


class DeployHttp(ffd.Service):
    _kernel: ffd.Kernel = None

    def __call__(self, port: int = 8080, **kwargs) -> Optional[Union[ffd.Message, object]]:
        self._kernel.run_device(ffi.HttpDevice(port=port))

        return True
