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
import uuid
from dataclasses import is_dataclass, fields, field, MISSING
from datetime import datetime, date
from typing import get_type_hints

import inflection
from firefly.domain.meta.context_aware import ContextAware
from firefly.domain.value_object import ValueObject, Empty


# noinspection PyDataclass
class Entity(ContextAware, ValueObject):
    _logger = None

    def __post_init__(self):
        if is_dataclass(self):
            missing = []
            types = get_type_hints(self.__class__)
            for field_ in fields(self):
                is_required = field_.metadata.get('required', False) is True
                has_no_value = getattr(self, field_.name) is None
                is_entity = inspect.isclass(types[field_.name]) and issubclass(types[field_.name], Entity)
                if is_required and has_no_value and not is_entity:
                    missing.append(field_.name)
            if len(missing) > 0:
                raise TypeError(f'{self.__class__.__name__}.__init__ missing {len(missing)} '
                                f'required argument(s): {", ".join(missing)}')

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
    def id_field(cls):
        if not is_dataclass(cls):
            raise TypeError('Entity::id_name() called on a non-dataclass entity')

        for field_ in fields(cls):
            if 'id' in field_.metadata:
                return field_

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
    metadata = {'id': True, 'required': True, 'type': str, 'is_uuid': is_uuid}
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
    return field(default=None, metadata=kwargs)


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
