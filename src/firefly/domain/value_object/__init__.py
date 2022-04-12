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

import firefly.domain.error as errors
import inflection
from firefly.domain.entity.validation import IsValidEmail, HasLength, MatchesPattern, IsValidUrl, IsLessThanOrEqualTo, \
    IsLessThan, IsGreaterThanOrEqualTo, IsGreaterThan, IsMultipleOf, HasMaxLength, HasMinLength, parse
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.meta.entity_meta import EntityMeta
from firefly.domain.utils import is_type_hint
from marshmallow import Schema, fields as m_fields, ValidationError, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.orm import Session

from .event_buffer import EventBuffer
from .generic_base import GenericBase
from .parameter import Parameter


class Empty:
    pass


_defs = {}


MARSHMALLOW_MAPPINGS = {
    str: m_fields.Str,
    int: m_fields.Int,
    float: m_fields.Float,
    bool: m_fields.Bool,
    datetime: m_fields.DateTime,
    date: m_fields.Date,
}


# noinspection PyDataclass
class ValueObject(metaclass=EntityMeta):
    _logger = None
    _session: Session = None
    _cache = None
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

    def to_dict(self, skip: list = None, force_all: bool = False, **kwargs):
        caller = kwargs.get('caller')
        include_relationships = kwargs.get('include_relationships', True)
        ret = self.schema().dump(self)

        if include_relationships:
            types = typing.get_type_hints(self.__class__)
            for field_ in fields(self):
                if field_.name.startswith('_'):
                    continue
                t = types[field_.name]
                if t is caller.__class__ and caller == getattr(self, field_.name):
                    continue
                if inspect.isclass(t) and issubclass(t, ValueObject):
                    try:
                        ret[field_.name] = getattr(self, field_.name).to_dict(
                            skip=skip, force_all=force_all, caller=self
                        )
                    except AttributeError:
                        pass
                elif is_type_hint(t) and get_origin(t) is list:
                    args = get_args(t)
                    if args[0] is caller.__class__:
                        continue
                    if inspect.isclass(args[0]) and issubclass(args[0], ValueObject):
                        try:
                            ret[field_.name] = [
                                e.to_dict(skip=skip, force_all=force_all, caller=self)
                                for e in getattr(self, field_.name)
                            ]
                        except AttributeError:
                            pass

        if skip is not None:
            for s in skip:
                if s in ret:
                    del ret[s]

        if force_all is False:
            for field in fields(self.__class__):
                if field.metadata.get('internal') is True:
                    del ret[field.name]

        return ret

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
    def validate(cls, data: dict):
        return cls.schema().validate(data)

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

        for k, v in list(data.items()).copy():
            if k.endswith('_'):
                data[str(k).rstrip('_')] = v
                del data[k]
        try:
            for k in list(data.keys()).copy():
                if k.startswith('_'):
                    del data[k]
            return cls.schema().load(data, session=cls._session, unknown=EXCLUDE, partial=True)
        except ValidationError as e:
            missing = list(filter(lambda f: not f.startswith('_'), e.args[0].keys()))
            if len(missing) > 0:
                raise errors.MissingArgument(
                    f"Missing {len(missing)} required argument(s) for class {cls.__name__}: {', '.join(missing)}"
                ) from e
            raise e

    @classmethod
    def schema(cls, stack: list = None) -> Schema:
        stack = stack or []
        if not isinstance(cls._cache, dict):
            cls._cache = {}

        if cls not in cls._cache:
            class FieldContainer(SQLAlchemyAutoSchema):
                class Meta:
                    model = cls
                    include_relationships = True
                    load_instance = True

            cls._cache[cls] = FieldContainer()

        return cls._cache[cls]

    def __str__(self):
        while True:
            try:
                return self.__repr__()
            except AttributeError as e:
                if 'object has no attribute' in str(e):
                    attr = str(e).split(' ')[-1].strip("'")
                    setattr(self, attr, None)
                else:
                    raise e
