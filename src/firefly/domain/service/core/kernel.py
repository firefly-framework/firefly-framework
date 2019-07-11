from __future__ import annotations

import firefly.domain as ffd


class Kernel:
    def __init__(self, device: ffd.Device):
        from firefly.application import Container
        # Inject our self into the container
        Container.kernel = lambda s: self
        Container.__annotations__['kernel'] = Kernel

        container = Container()
        self._bus = container.system_bus

        self._config = container.configuration
        self._context_map = container.context_map

        self._device = device
        self._device._bus = self._bus

        self._ports = []

        self._context_map.initialize()

    def run(self):
        self._device.run()

    def run_device(self, device: ffd.Device):
        device._bus = self._bus
        for port in self._ports:
            device.register_port(**port)
        device.run()

    def register_port(self, cmd: ffd.Command):
        self._ports.append(cmd)
        self._device.register_port(cmd)
