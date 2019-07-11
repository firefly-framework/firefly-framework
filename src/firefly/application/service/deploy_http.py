from __future__ import annotations

import firefly.domain as ffd
import firefly.infrastructure as ffi


class DeployHttp(ffd.Service):
    _kernel: ffd.Kernel = None

    def __call__(self, port: int = 8080, **kwargs):
        self._kernel.run_device(ffi.HttpDevice(port=port))
