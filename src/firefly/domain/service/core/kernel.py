from __future__ import annotations

from typing import Callable

import firefly.domain as ffd


class Kernel:
    def __init__(self, hub: ffd.Hub):
        from firefly.application import Container
        # Inject our self into the container
        Container.kernel = lambda s: self
        Container.__annotations__['kernel'] = Kernel

        container = Container()
        self._bus = container.message_bus
        self._bus.add(self._listener)

        self._config = container.configuration
        self._context_map = container.context_map

        self._hub = hub
        self._hub._bus = self._bus

        self._context_map.initialize()

    def run(self):
        self._hub.run()

    def register_port(self, **kwargs):
        self._hub.register_port(**kwargs)

    def _listener(self, message: ffd.Message, next_: Callable):
        if isinstance(message, ffd.RegisterPresentationMiddleware):
            self._bus.add(message.body())

        return next_(message)
