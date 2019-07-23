from __future__ import annotations

from typing import Union

import firefly.domain as ffd


class Kernel:
    def __init__(self, container=None):
        if container is None:
            from firefly.application import Container
            container = Container()

        c = container.__class__
        # Inject our self into the container
        c.kernel = lambda s: self
        c.__annotations__['kernel'] = Kernel

        self._bus = container.system_bus
        self._config = container.configuration
        self._context_map = container.context_map
        self._container = container

        self._ports = []

        self._context_map.initialize()

    def run(self, device: Union[str, ffd.Device]):
        if isinstance(device, str):
            device = getattr(self._container, device)
        device.run()
