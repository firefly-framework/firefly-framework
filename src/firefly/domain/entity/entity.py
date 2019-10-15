from __future__ import annotations

import enum
import uuid
from dataclasses import is_dataclass, fields, field, MISSING, asdict
from datetime import datetime, date

import inflection

from ..utils import EntityMeta


# noinspection PyDataclass
class Entity(metaclass=EntityMeta):
    def __init__(self, **kwargs):
        pass

    def __post_init__(self):
        if is_dataclass(self):
            missing = []
            for field_ in fields(self):
                if 'required' in field_.metadata and isinstance(getattr(self, field_.name), Empty):
                    missing.append(field_.name)
            if len(missing) > 0:
                raise TypeError(f'__init__ missing {len(missing)} required argument(s): {", ".join(missing)}')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.id_value() == other.id_value()

    def id_value(self):
        if not is_dataclass(self):
            raise TypeError('Entity::id_value() called on a non-dataclass entity')

        for field_ in fields(self):
            if 'id' in field_.metadata:
                return getattr(self, field_.name)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def id_name(cls):
        if not is_dataclass(cls):
            raise TypeError('Entity::id_name() called on a non-dataclass entity')

        for field_ in fields(cls):
            if 'id' in field_.metadata:
                return field_.name

    @classmethod
    def match_id_from_argument_list(cls, args: dict):
        snake = f'{inflection.underscore(cls.__name__)}_id'
        if snake in args:
            return {snake: args[snake]}

        id_name = cls.id_name()
        if id_name in args:
            return {id_name: args[id_name]}


class Empty:
    pass


def id_(is_uuid: bool = True, **kwargs):
    metadata = {'id': True}
    if is_uuid:
        metadata['length'] = 36
    metadata.update(kwargs)
    return field(default_factory=lambda: str(uuid.uuid1()), metadata=metadata) if is_uuid else \
        required(**metadata)


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


def hidden(**kwargs):
    return field(default=None, init=False, repr=False, compare=False, metadata=kwargs)
