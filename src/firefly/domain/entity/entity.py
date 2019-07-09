from __future__ import annotations

import inspect
import uuid
from abc import ABC
from dataclasses import is_dataclass, fields, field, MISSING
from datetime import datetime, date
from typing import get_type_hints

import firefly.domain as ffd


class Entity(ABC):
    event_buffer: ffd.EventBuffer = None

    def dispatch(self, event: ffd.Event):
        self.event_buffer.append(event)

    def __post_init__(self):
        if not is_dataclass(self):
            return

        missing = []
        for field_ in fields(self):
            if 'required' in field_.metadata and isinstance(getattr(self, field_.name), Empty):
                missing.append(field_.name)
        if len(missing) > 0:
            raise TypeError(f'__init__ missing {len(missing)} required argument(s): {", ".join(missing)}')

    @classmethod
    def get_params(cls, op: str):
        if not is_dataclass(cls):
            raise TypeError('get_params called on a non-dataclass entity')

        if op in ('create', 'update'):
            return cls._get_create_update_params()
        else:
            types = get_type_hints(cls)
            for field_ in fields(cls):
                if 'pk' in field_.metadata:
                    return {field_.name: {
                        'default': inspect.Parameter.empty,
                        'type': types[field_.name],
                    }}

    @classmethod
    def _get_create_update_params(cls):
        ret = {}
        for field_ in fields(cls):
            types = get_type_hints(cls)
            default = inspect.Parameter.empty
            if field_.default != MISSING:
                default = field_.default
            elif field_.default_factory != MISSING:
                default = field_.default_factory()
            if 'required' in field_.metadata:
                default = inspect.Parameter.empty

            ret[field_.name] = {
                'default': default,
                'type': types[field_.name],
            }

        return ret


class Empty:
    pass


def pk(**kwargs):
    metadata = {'pk': True}
    metadata.update(kwargs)
    return field(default_factory=lambda: str(uuid.uuid1()), metadata=metadata)


def list_(**kwargs):
    return field(default_factory=lambda: [], metadata=kwargs)


def dict_(**kwargs):
    return field(default_factory=lambda: {}, metadata=kwargs)


def now(**kwargs):
    return field(default_factory=lambda: datetime.now(), metadata=kwargs)


def today(**kwargs):
    return field(default_factory=lambda: date.today(), metadata=kwargs)


def required(**kwargs):
    metadata = {'required': True}
    metadata.update(kwargs)
    return field(default_factory=lambda: Empty(), metadata=metadata)


def optional(**kwargs):
    return field(default=None, metadata=kwargs)
