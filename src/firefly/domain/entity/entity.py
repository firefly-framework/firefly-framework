#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

import inspect
import typing
from datetime import datetime, date

import inflection

from .validation import *
from firefly.domain.value_object import ValueObject, Empty
from firefly.domain.meta.context_aware import ContextAware
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.utils import is_type_hint, get_origin, get_args

# __pragma__('skip')
import uuid

from dataclasses import is_dataclass, fields, field, MISSING
from typing import List, Callable
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import is_dataclass, fields, field, MISSING, asdict, List, Callable, uuid
?"""
# __pragma__ ('noecom')
# __pragma__('kwargs')


# noinspection PyDataclass
class Entity(ContextAware, ValueObject):
    _logger = None

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

        ret = []
        for field_ in fields(self):
            if 'id' in field_.metadata:
                ret.append(getattr(self, field_.name))

        return ret[0] if len(ret) == 1 else ret

    def load_dict(self, data: dict):
        data = build_argument_list(data, self.__class__, strict=False)
        t = typing.get_type_hints(self.__class__)
        for name, type_ in t.items():
            if name in data:
                if inspect.isclass(type_) and issubclass(type_, (datetime, date)) and isinstance(data[name], str):
                    setattr(self, name, parse(data[name], ignoretz=True))
                else:
                    try:
                        if data[name] is not None and not isinstance(data[name], type_):
                            setattr(self, name, type_(data[name]))
                        else:
                            setattr(self, name, data[name])
                    except TypeError:
                        setattr(self, name, data[name])

    @classmethod
    def id_name(cls):
        if not is_dataclass(cls):
            raise TypeError('Entity::id_name() called on a non-dataclass entity')

        ret = []
        for field_ in fields(cls):
            if 'id' in field_.metadata:
                ret.append(field_.name)

        return ret[0] if len(ret) == 1 else ret

    @classmethod
    def match_id_from_argument_list(cls, args: dict):
        snake = f'{inflection.underscore(cls.__name__)}_id'
        if snake in args:
            return {snake: args[snake]}

        id_name = cls.id_name()
        if id_name in args:
            return {id_name: args[id_name]}

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)


def id_(is_uuid: bool = True, **kwargs):
    metadata = {'id': True, 'required': True, 'type': str}
    if is_uuid:
        metadata['length'] = 36
    metadata.update(kwargs)
    return field(default_factory=lambda: str(uuid.uuid4()), metadata=metadata) if is_uuid else \
        required(**metadata)


def list_(**kwargs):
    kwargs['type'] = list
    return field(default_factory=lambda: [], metadata=kwargs)


def dict_(**kwargs):
    kwargs['type'] = dict
    return field(default_factory=lambda: {}, metadata=kwargs)


def now(**kwargs):
    kwargs['type'] = datetime
    return field(default_factory=lambda: datetime.now(), metadata=kwargs)


def today(**kwargs):
    kwargs['type'] = date
    return field(default_factory=lambda: date.today(), metadata=kwargs)


def required(type_: type = None, **kwargs):
    if type_ is not None:
        kwargs['type'] = type_
    kwargs['required'] = True
    return field(default_factory=lambda: Empty(), metadata=kwargs)


def optional(type_: type = None, default=MISSING, **kwargs):
    if type_ is not None:
        kwargs['type'] = type_
    kwargs['required'] = False
    if not isinstance(default, MISSING.__class__):
        return field(default_factory=lambda: default, metadata=kwargs)
    return field(default=None, metadata=kwargs)


def hidden(**kwargs):
    kwargs['hidden'] = True
    return field(default=None, init=False, repr=False, compare=False, metadata=kwargs)
