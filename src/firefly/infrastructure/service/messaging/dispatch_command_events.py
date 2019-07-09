from __future__ import annotations

from typing import Callable

import firefly.domain as ffd


@ffd.command_handler()
class DispatchCommandEvents(ffd.Middleware, ffd.SystemBusAware):
    _event_buffer: ffd.EventBuffer = None

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        try:
            ret = next_(message)
            for event in self._event_buffer:
                self.dispatch(event)
        finally:
            self._event_buffer.clear()

        return ret
