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

import typing
from datetime import datetime, date

import inflection

from firefly.domain.meta.entity_meta import EntityMeta
from firefly.domain.meta.context_aware import ContextAware
from firefly.domain.meta.build_argument_list import build_argument_list

# __pragma__('skip')
import uuid

from dataclasses import is_dataclass, fields, field, MISSING, asdict
from typing import List, Callable
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.ui.web.polyfills import is_dataclass, fields, field, MISSING, asdict, List, Callable, uuid
?"""
# __pragma__ ('noecom')
# __pragma__('kwargs')


# noinspection PyDataclass
class Entity(ContextAware, metaclass=EntityMeta):
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

    def load_dict(self, data: dict):
        data = self._process_data(self.__class__, data)
        t = typing.get_type_hints(self.__class__)
        for name, type_ in t.items():
            setattr(self, name, data[name])

    @staticmethod
    def _process_data(cls, data: dict):
        t = typing.get_type_hints(cls)
        for name, type_ in t.items():
            if name.startswith('_'):
                continue

            if isinstance(type_, type(List)):
                new_list = []
                for item in data[name]:
                    nested_data = Entity._process_data(type_.__args__[0], item)
                    new_list.append(type_.__args__[0](**build_argument_list(nested_data, type_.__args__[0])))
                data[name] = new_list
            else:
                try:
                    if issubclass(type_, Entity):
                        data[name] = type_(**build_argument_list(data[name], type_))
                except TypeError:
                    pass

        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls._construct_entity(cls, data)

    @staticmethod
    def _construct_entity(cls: typing.Type[Entity], data: dict):
        t = typing.get_type_hints(cls)
        for name, type_ in t.items():
            if name.startswith('_'):
                continue

            if isinstance(type_, type(List)):
                new_list = []
                for item in data[name]:
                    new_list.append(Entity._construct_entity(type_.__args__[0], item))
                data[name] = new_list
            else:
                try:
                    if issubclass(type_, Entity):
                        data[name] = type_(**build_argument_list(data[name], type_))
                except TypeError:
                    pass

        return cls(**build_argument_list(data, cls))

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
    metadata = {'id': True, 'required': True, 'type': str}
    if is_uuid:
        metadata['length'] = 36
    metadata.update(kwargs)
    return field(default_factory=lambda: str(uuid.uuid1()), metadata=metadata) if is_uuid else \
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
