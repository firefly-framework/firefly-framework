from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from dataclasses import make_dataclass

import firefly.domain as ffd

from ..messaging.system_bus import SystemBusAware


class Service(ABC, SystemBusAware):
    @abstractmethod
    def __call__(self, **kwargs):
        pass

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
