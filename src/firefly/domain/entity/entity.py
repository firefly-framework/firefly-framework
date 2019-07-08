from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import is_dataclass, fields, field
from datetime import datetime, date


class Entity(ABC):
    def __post_init__(self):
        if not is_dataclass(self):
            return
        missing = []
        for field_ in fields(self):
            if 'required' in field_.metadata and isinstance(getattr(self, field_.name), Empty):
                missing.append(field_.name)
        if len(missing) > 0:
            raise TypeError(f'__init__ missing {len(missing)} required argument(s): {", ".join(missing)}')


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
