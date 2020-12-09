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

# __pragma__('skip')
from __future__ import annotations

import inspect
import typing
from dataclasses import fields
from datetime import datetime, date
from typing import List, Union, Dict

import inflection
from firefly.domain.entity.validation import IsValidEmail, HasLength, MatchesPattern, IsValidUrl, IsLessThanOrEqualTo, \
    IsLessThan, IsGreaterThanOrEqualTo, IsGreaterThan, IsMultipleOf, HasMaxLength, HasMinLength
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.meta.entity_meta import EntityMeta
from firefly.domain.utils import is_type_hint, get_origin, get_args, can_be_type

from .event_buffer import EventBuffer
from .generic_base import GenericBase
from .parameter import Parameter


class Empty:
    pass


_defs = {}


# noinspection PyDataclass
class ValueObject(metaclass=EntityMeta):
    _logger = None
    _mappings = {
        str: 'string',
        int: 'integer',
        float: 'number',
        bool: 'boolean',
        datetime: 'string',
        date: 'string',
    }

    def __init__(self, **kwargs):
        pass

    def to_dict(self, skip: list = None, force_all: bool = False):
        ret = {}
        annotations_ = typing.get_type_hints(self.__class__)
        for field_ in fields(self):
            if field_.name.startswith('_'):
                continue
            if field_.metadata.get('internal') is True and force_all is False:
                continue

            type_ = annotations_[field_.name]
            if inspect.isclass(type_) and issubclass(type_, ValueObject):
                f = getattr(self, field_.name)
                if isinstance(f, ValueObject):
                    ret[field_.name] = f.to_dict()
                else:
                    ret[field_.name] = None
            elif is_type_hint(annotations_[field_.name]):
                origin = get_origin(type_)
                args = get_args(type_)
                if origin is List and can_be_type(args[0], ValueObject):
                    if getattr(self, field_.name) is None:
                        ret[field_.name] = None
                    else:
                        ret[field_.name] = list(map(
                            lambda v: v.to_dict() if isinstance(v, ValueObject) else None,
                            getattr(self, field_.name)
                        ))
                elif origin is Dict and can_be_type(args[1], ValueObject):
                    if getattr(self, field_.name) is None:
                        ret[field_.name] = None
                    else:
                        ret[field_.name] = {k: v.to_dict() for k, v in getattr(self, field_.name).items()}
                else:
                    ret[field_.name] = getattr(self, field_.name)
            else:
                ret[field_.name] = getattr(self, field_.name)

        if skip is not None:
            d = ret.copy()
            for k in ret.keys():
                if k in skip:
                    del d[k]
            return d

        return ret

    @classmethod
    def get_dto_schema(cls, stack: List[type] = None):
        global _defs

        stack = stack or []
        if len(stack) == 0:
            _defs = {}

        if cls in stack or cls.__name__ in _defs:
            if cls.__name__ not in _defs:
                _defs[cls.__name__] = {}
            return _defs[cls.__name__]

        stack.append(cls)

        ret = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'title': cls.__name__,
            'type': 'object',
        }

        types_ = typing.get_type_hints(cls)
        props = {}
        required_fields = []
        for field_ in fields(cls):
            if field_.name.startswith('_'):
                continue

            if 'hidden' in field_.metadata and field_.metadata['hidden'] is True:
                continue

            prop = {
                'title': field_.metadata.get('title') or inflection.humanize(field_.name),
            }
            t = types_[field_.name]
            if t in cls._mappings:
                if t in cls._mappings:
                    prop['type'] = cls._mappings[t]

            if is_type_hint(t):
                prop = cls._process_type_hint(t, prop, stack)
            elif inspect.isclass(t) and issubclass(t, ValueObject):
                prop['type'] = 'object'
                subclasses = t.__subclasses__()
                if len(subclasses):
                    prop['items'] = {'oneOf': []}
                    for subclass in subclasses:
                        subclass.get_dto_schema(stack.copy())
                        prop['items']['oneOf'].append({'$ref': f'#/definitions/{subclass.__name__}'})
                else:
                    t.get_dto_schema(stack.copy())
                    prop = {'$ref': f'#/definitions/{t.__name__}'}

            if 'validators' in field_.metadata:
                for validator in field_.metadata['validators']:
                    if isinstance(validator, IsValidEmail):
                        prop['format'] = 'email'
                    elif isinstance(validator, HasLength):
                        prop['minLength'] = validator.length
                        prop['maxLength'] = validator.length
                    elif isinstance(validator, MatchesPattern):
                        prop['pattern'] = validator.regex
                    elif isinstance(validator, IsValidUrl):
                        prop['format'] = 'uri'
                    elif isinstance(validator, IsLessThanOrEqualTo):
                        prop['maximum'] = validator.value
                    elif isinstance(validator, IsLessThan):
                        prop['maximum'] = validator.value
                        prop['exclusiveMaximum'] = True
                    elif isinstance(validator, IsGreaterThanOrEqualTo):
                        prop['minimum'] = validator.value
                    elif isinstance(validator, IsGreaterThan):
                        prop['minimum'] = validator.value
                        prop['exclusiveMinimum'] = True
                    elif isinstance(validator, IsMultipleOf):
                        prop['multipleOf'] = validator.value
                    elif isinstance(validator, HasMaxLength):
                        prop['maxLength'] = validator.length
                    elif isinstance(validator, HasMinLength):
                        prop['minLength'] = validator.length

            if t is datetime:
                prop['format'] = 'date-time'
            elif t is date:
                prop['format'] = 'date'

            if 'format' in field_.metadata:
                prop['format'] = field_.metadata.get('format')

            if 'required' in field_.metadata and field_.metadata['required'] is True:
                try:
                    if isinstance(field_.default_factory(), Empty):
                        required_fields.append(field_.name)
                except TypeError:
                    required_fields.append(field_.name)

            else:
                prop['default'] = None

            props[field_.name] = prop

        ret['properties'] = props
        if len(required_fields) > 0:
            ret['required'] = required_fields

        if len(stack) == 1:
            ret['definitions'] = _defs
        else:
            _defs[cls.__name__] = ret
            return {'$ref': f'#/definitions/{cls.__name__}'}

        return ret

    @classmethod
    def _process_type_hint(cls, obj, config: dict, stack: list):
        if not is_type_hint(obj):
            return config

        if get_origin(obj) is List:
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

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)

    @classmethod
    def from_dict(cls, data: dict, map_: dict = None, skip: list = None):
        if map_ is not None:
            d = data.copy()
            for source, target in map_.items():
                if source in d:
                    d[target] = d[source]
            data = d

        if skip is not None:
            d = data.copy()
            for k in data.keys():
                if k in skip:
                    del d[k]
            data = d

        return cls(**build_argument_list(data, cls))
    # __pragma__('noskip')
