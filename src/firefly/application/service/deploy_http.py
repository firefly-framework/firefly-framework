from __future__ import annotations

import firefly.domain as ffd
import firefly.infrastructure as ffi


class DeployHttp(ffd.Service):
    _kernel: ffd.Kernel = None
    _http_device: ffi.HttpDevice = None

    def __call__(self, port: int = 8080, **kwargs):
        self._http_device.port = port
        self._kernel.run(self._http_device)
