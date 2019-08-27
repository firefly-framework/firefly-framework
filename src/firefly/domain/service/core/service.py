from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import make_dataclass
from typing import List, Union, Tuple

import firefly.domain as ffd

from ..messaging.system_bus import SystemBusAware


class Service(ABC, SystemBusAware):
    _event_buffer: ffd.EventBuffer = None

    @abstractmethod
    def __call__(self, **kwargs):
        pass

    def _process_events(self, events):
        if isinstance(events, list):
            for event in events:
                if isinstance(event, (ffd.Event, tuple)):
                    self._event_buffer.append(event)
        elif isinstance(events, tuple) and len(events) == 2:
            self._event_buffer.append(events)

        return events

    @classmethod
    def get_message(cls):
        if not hasattr(cls, '__ff_message'):
            sig = inspect.signature(cls.__call__)
            base = ffd.Query
            if sig.return_annotation in ('None', inspect.Signature.empty):
                base = ffd.Command

            fields = []
            for name, config in cls.get_arguments().items():
                fields.append((name, config['type'], config['default']))

            setattr(cls, '__ff_message', make_dataclass(cls.__name__, fields, bases=(base,)))

        return getattr(cls, '__ff_message')

    @classmethod
    def get_arguments(cls) -> dict:
        return ffd.get_arguments(cls.__call__)
