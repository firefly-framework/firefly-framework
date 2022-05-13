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

import inspect
import typing
from dataclasses import fields
from datetime import datetime, date
from typing import List, Union, Dict
from typing import get_origin, get_args

import inflection
from pydantic import BaseModel
from sqlalchemy.exc import InvalidRequestError

import firefly.domain as ffd
from firefly.domain.entity.validation.validators import IsValidEmail, HasLength, MatchesPattern, IsValidUrl, \
    IsLessThanOrEqualTo, IsLessThan, IsGreaterThanOrEqualTo, IsGreaterThan, IsMultipleOf, HasMaxLength, HasMinLength, \
    parse
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.utils import is_type_hint
from .event_buffer import EventBuffer
from .generic_base import GenericBase
from .parameter import Parameter


class Empty:
    pass


_defs = {}


# noinspection PyDataclass
class ValueObject(BaseModel):
    def __init__(self, **kwargs):
        pass

    def to_dict(self):
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**ffd.build_argument_list(data, cls))

    def load_dict(self, d: dict):
        data = build_argument_list(d.copy(), self.__class__, strict=False, include_none_parameters=True)
        t = typing.get_type_hints(self.__class__)
        for name, type_ in t.items():
            if name in data:
                if inspect.isclass(type_) and issubclass(type_, (datetime, date)) and isinstance(data[name], str):
                    setattr(self, name, parse(data[name], ignoretz=True))
                elif inspect.isclass(type_) and issubclass(type_, ValueObject) and isinstance(data[name], type_):
                    existing = getattr(self, name)
                    if existing is None:
                        setattr(self, name, data[name])
                    elif name in d and isinstance(d[name], dict):
                        existing.load_dict(d[name])
                else:
                    try:
                        if data[name] is not None and not isinstance(data[name], type_):
                            setattr(self, name, type_(data[name]))
                        else:
                            setattr(self, name, data[name])
                    except TypeError:
                        setattr(self, name, data[name])

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)

    @classmethod
    def _process_type_hint(cls, obj, config: dict, stack: list):
        if not is_type_hint(obj):
            return config

        if get_origin(obj) is list:
            config['type'] = 'array'
            args = get_args(obj)
            if inspect.isclass(args[0]) and issubclass(args[0], ValueObject):
                subclasses = args[0].__subclasses__()
                if len(subclasses):
                    config['items'] = {'oneOf': []}
                    for subclass in subclasses:
                        subclass.get_dto_schema(stack.copy())
                        config['items']['oneOf'].append({'$ref': f'#/definitions/{subclass.__name__}'})
                else:
                    args[0].get_dto_schema(stack.copy())
                    config['items'] = {'$ref': f'#/definitions/{args[0].__name__}'}

            elif is_type_hint(args[0]):
                config['items'] = cls._process_type_hint(args[0], {}, stack)['items']

            elif args[0] in cls._mappings:
                config['items'] = {
                    'type': cls._mappings[args[0]]
                }

        elif get_origin(obj) is Dict:
            args = get_args(obj)
            config['type'] = 'object'
            if 'properties' in config:
                del config['properties']

            if is_type_hint(args[1]):
                options = cls._process_type_hint(args[1], {}, stack)
            elif inspect.isclass(args[1]) and issubclass(args[1], ValueObject):
                args[1].get_dto_schema(stack.copy())
                options = {'$ref': f'#/definitions/{args[1].__name__}'}
            else:
                options = {'type': cls._mappings[args[1]]}

            config['patternProperties'] = {
                r'.*': options
            }

        elif get_origin(obj) is Union:
            args = get_args(obj)
            config['items'] = {'oneOf': []}
            for arg in args:
                if is_type_hint(arg):
                    raise NotImplementedError()
                elif inspect.isclass(arg) and issubclass(arg, ValueObject):
                    arg.get_dto_schema(stack.copy())
                    config['items']['oneOf'].append({'$ref': f'#/definitions/{arg.__name__}'})
                elif arg in cls._mappings:
                    config['items']['oneOf'].append({'type': cls._mappings[arg]})

        return config

    def __str__(self):
        while True:
            try:
                return self.__repr__()
            except InvalidRequestError:
                ret = self.__class__.__name__ + '('
                props = []
                for f in fields(self):
                    props.append(f"{f.name}={getattr(self, f.name)}")
                return f"{self.__class__.__name__}({', '.join(props)})"
            except AttributeError as e:
                if 'object has no attribute' in str(e):
                    attr = str(e).split(' ')[-1].strip("'")
                    setattr(self, attr, None)
                else:
                    raise e
