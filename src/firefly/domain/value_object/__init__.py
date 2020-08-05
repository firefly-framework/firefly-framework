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

import typing
from dataclasses import fields
from datetime import datetime, date
from typing import List

import inflection
from firefly.domain.entity.validation import IsValidEmail, HasLength, MatchesPattern, IsValidUrl, IsLessThanOrEqualTo, \
    IsLessThan, IsGreaterThanOrEqualTo, IsGreaterThan, IsMultipleOf, HasMaxLength, HasMinLength
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.meta.entity_meta import EntityMeta

from .event_buffer import EventBuffer
from .generic_base import GenericBase
from .parameter import Parameter


class Empty:
    pass


# noinspection PyDataclass
class ValueObject(metaclass=EntityMeta):
    _logger = None

    def __init__(self, **kwargs):
        pass

    def to_dict(self, skip: list = None, force_all: bool = False):
        ret = {}
        for field_ in fields(self):
            if field_.name.startswith('_'):
                continue
            if field_.metadata.get('internal') is True and force_all is False:
                continue
            ret[field_.name] = getattr(self, field_.name)

        if skip is not None:
            d = ret.copy()
            for k in ret.keys():
                if k in skip:
                    del d[k]
            return d

        return ret

    @classmethod
    def get_dto_schema(cls):
        ret = {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'title': cls.__name__,
            'type': 'object',
        }

        mappings = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            datetime: 'string',
            date: 'string',
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
            if t in mappings:
                if t in mappings:
                    prop['type'] = mappings[t]

            if isinstance(t, type(List)):
                prop['type'] = 'array'
                if issubclass(t.__args__[0], ValueObject):
                    prop['items'] = t.__args__[0].get_dto_schema()
                elif t.__args__[0] in mappings:
                    prop['items'] = {
                        'type': mappings[t.__args__[0]]
                    }

            try:
                if issubclass(t, ValueObject):
                    s = t.get_dto_schema()
                    prop['type'] = 'object'
                    prop['properties'] = s['properties']
            except TypeError:
                pass

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
                # props[field_.name] = prop

            else:
                prop['default'] = None
            #     if prop['type'] not in ('array',):
            #         prop['type'] = [prop['type'], 'null']
                # nested = prop.copy()
                # del nested['title']
                # props[field_.name] = {
                #     'title': prop['title'],
                #     'oneOf': [nested, {'type': 'null'}]
                # }

            props[field_.name] = prop

        ret['properties'] = props
        if len(required_fields) > 0:
            ret['required'] = required_fields

        return ret

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
