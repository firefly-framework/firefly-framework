from __future__ import annotations

from typing import Callable

import firefly.domain as ffd


class Kernel:
    def __init__(self, device: ffd.Device):
        from firefly.application import Container
        # Inject our self into the container
        Container.kernel = lambda s: self
        Container.__annotations__['kernel'] = Kernel

        container = Container()
        self._bus = container.system_bus
        self._bus.add_command_handler(self._command_handler)

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

    def register_port(self, **kwargs):
        self._ports.append(kwargs)
        self._device.register_port(**kwargs)

    def _command_handler(self, message: ffd.Message, next_: Callable):
        if isinstance(message, ffd.RegisterPresentationMiddleware):
            self._bus.add_query_handler(message.body())

        return next_(message)
