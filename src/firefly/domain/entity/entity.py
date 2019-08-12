from __future__ import annotations

import inspect
import uuid
from abc import ABC
from dataclasses import is_dataclass, fields, field, MISSING
from datetime import datetime, date
from typing import get_type_hints, Union

import firefly.domain as ffd


class Entity(ABC):
    event_buffer: ffd.EventBuffer = None

    def dispatch(self, event: Union[ffd.Event, str], data: dict = None):
        if isinstance(event, str):
            self.event_buffer.append((event, data))
        else:
            self.event_buffer.append(event)

    def __post_init__(self):
        if is_dataclass(self):
            missing = []
            # noinspection PyDataclass
            for field_ in fields(self):
                if 'required' in field_.metadata and isinstance(getattr(self, field_.name), Empty):
                    missing.append(field_.name)
            if len(missing) > 0:
                raise TypeError(f'__init__ missing {len(missing)} required argument(s): {", ".join(missing)}')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.pk_value() == other.pk_value()

    def pk_value(self):
        # noinspection PyDataclass
        for field_ in fields(self):
            if 'pk' in field_.metadata:
                return getattr(self, field_.name)

    @classmethod
    def get_params(cls, op: str):
        if not is_dataclass(cls):
            raise TypeError('get_params called on a non-dataclass entity')

        if op in ('create', 'update'):
            return cls._get_create_update_params()
        else:
            types = get_type_hints(cls)
            # noinspection PyDataclass
            for field_ in fields(cls):
                if 'pk' in field_.metadata:
                    return {field_.name: {
                        'default': inspect.Parameter.empty,
                        'type': types[field_.name],
                    }}

    @classmethod
    def _get_create_update_params(cls):
        ret = {}
        # noinspection PyDataclass
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


def id(**kwargs):
    metadata = {'pk': True, 'length': 36}
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


def optional(default=MISSING, **kwargs):
    if default != MISSING:
        return field(default_factory=lambda: default, metadata=kwargs)
    return field(default=None, metadata=kwargs)
