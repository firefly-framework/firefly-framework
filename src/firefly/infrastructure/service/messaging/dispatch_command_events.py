from __future__ import annotations

from typing import Callable

import firefly.domain as ffd


@ffd.command_handler()
class DispatchCommandEvents(ffd.Middleware, ffd.SystemBusAware):
    _event_buffer: ffd.EventBuffer = None
    _message_factory: ffd.MessageFactory = None

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        try:
            ret = next_(message)
            for event in self._event_buffer:
                if isinstance(event, tuple):
                    self.dispatch(self._message_factory.event(event[0], event[1]))
                else:
                    self.dispatch(event)
        finally:
            self._event_buffer.clear()

        return ret
