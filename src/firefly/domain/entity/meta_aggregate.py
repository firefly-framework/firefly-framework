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

from dataclasses import fields
from typing import List, Any

import firefly.domain.entity as e
import inflection

from .aggregate_root import AggregateRoot
from .entity import id_, required, hidden, IsOneOf, IsMultipleOf, IsLessThanOrEqualTo, IsLessThan, \
    IsGreaterThanOrEqualTo, IsGreaterThan, HasMaxLength, HasMinLength, MatchesPattern, Entity, list_
from .json_schema import JsonSchema
from ..meta.entity_meta import EntityMeta


class MetaAggregate(AggregateRoot):
    id: str = id_()
    schema: JsonSchema = required()
    data: dict = required()
    _obj: AggregateRoot = hidden()

    def __getattr__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            try:
                return object.__getattribute__(super(), item)
            except AttributeError:
                return getattr(self._obj, item)

    def __setattr__(self, key, value):
        try:
            object.__setattr__(self, key, value)
        except AttributeError:
            try:
                object.__setattr__(super(), key, value)
            except AttributeError:
                setattr(self._obj, key, value)

    def __post_init__(self):
        if self._obj is None:
            self._obj = self._build_entity(self.schema.schema).from_dict(self.data)

    @classmethod
    def _build_entity(cls, schema: dict, name: str = None):
        class_name = name or inflection.camelize(schema['title'].replace(' ', ''))
        props, annotations_ = cls._process_json_schema_properties(schema)
        props['__annotations__'] = annotations_

        return EntityMeta.__new__(EntityMeta, class_name, (Entity,), props, fields_=props, annotations_=annotations_)

    @classmethod
    def _process_json_schema_properties(cls, schema: dict, props: dict = None, annotations_: dict = None):
        props = props or {}
        annotations_ = annotations_ or {}

        for k, v in schema['properties'].items():
            key = inflection.underscore(k)
            prop, annotation = cls._process_property(
                v, 'required' in schema and k in schema['required'], key
            )
            props[key] = prop
            annotations_[key] = annotation

        return props, annotations_

    @classmethod
    def _process_property(cls, schema: dict, required: bool, key: str):
        t = e.required if required else e.optional
        params = {}

        if 'default' in schema:
            params['default'] = schema['default']

        validators = cls._get_validators(schema)
        if len(validators) > 0:
            params['validators'] = validators

        if 'const' in schema:
            return schema['const'], Any

        if 'type' not in schema:
            return t(**params), Any

        if schema['type'] == 'integer':
            return t(**params), int

        if schema['type'] == 'number':
            return t(**params), float

        if schema['type'] == 'null':
            return t(**params), None

        if schema['type'] == 'boolean':
            return t(**params), bool

        if schema['type'] == 'string':
            return t(**params), str

        if schema['type'] == 'array':
            f, type_ = cls._process_property(schema['items'], False, inflection.singularize(key))
            return list_(**params), List[type_]

        if schema['type'] == 'object':
            cls = cls._build_entity(schema, inflection.camelize(key))
            return t(**params), cls

        raise NotImplementedError(f"Don't know how to parse property: {schema}")

    @classmethod
    def _get_validators(cls, schema: dict):
        ret = []

        if 'enum' in schema:
            ret.append(IsOneOf(schema['enum']))

        if 'multipleOf' in schema:
            ret.append(IsMultipleOf(schema['multipleOf']))

        if 'maximum' in schema:
            ret.append(IsLessThanOrEqualTo(schema['maximum']))

        if 'exclusiveMaximum' in schema:
            ret.append(IsLessThan(schema['exclusiveMaximum']))

        if 'minimum' in schema:
            ret.append(IsGreaterThanOrEqualTo(schema['minimum']))

        if 'exclusiveMinimum' in schema:
            ret.append(IsGreaterThan(schema['exclusiveMinimum']))

        if 'maxLength' in schema:
            ret.append(HasMaxLength(schema['maxLength']))

        if 'minLength' in schema:
            ret.append(HasMinLength(schema['minLength']))

        if 'pattern' in schema:
            ret.append(MatchesPattern(schema['pattern']))

        # TODO Array and Object validators
        # https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.6

        return ret
