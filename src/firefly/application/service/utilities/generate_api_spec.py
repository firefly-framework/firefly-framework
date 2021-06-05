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
import json
from dataclasses import fields, is_dataclass
from datetime import datetime, date
from typing import Type, List

import firefly.domain as ffd
import inflection
import typing


@ffd.cli('firefly generate api-spec')
class GenerateApiSpec(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None

    def __init__(self):
        self._schemas = []

    def __call__(self, tag: str = None, **kwargs):
        try:
            from apispec import APISpec
            from docstring_parser import parse
        except ModuleNotFoundError:
            raise ffd.MissingDependency('This feature requires "apispec" and "docstring_parser"')

        self._spec = APISpec(
            title='Testing Spec',
            version='1.0.0',
            openapi_version='3.0.2',
        )

        for context in self._context_map.contexts:
            prefix = f'/{inflection.dasherize(context.name)}'
            for endpoint in context.endpoints:
                if isinstance(endpoint, ffd.HttpEndpoint):
                    if tag is not None and tag not in endpoint.tags:
                        continue
                    docstring = parse(endpoint.service.__call__.__doc__)
                    short_description = docstring.short_description \
                        if docstring.short_description != 'Call self as a function.' else None

                    path = endpoint.route
                    if not path.startswith(prefix):
                        path = f'{prefix}{path}'

                    request_body = self._request_body(endpoint)
                    method = endpoint.method.lower()
                    operations = {method: {}}
                    if request_body is not None:
                        operations[method]['requestBody'] = request_body
                    self._spec.path(
                        path=path,
                        operations=operations,
                        parameters=self._parameter_list(endpoint)
                    )

        print(json.dumps(self._spec.to_dict(), indent=2))

    def _parameter_list(self, endpoint: ffd.HttpEndpoint):
        ret = []
        if inspect.isclass(endpoint.service) and issubclass(endpoint.service, ffd.AggregateRoot):
            if endpoint.method.lower() == 'post':
                return [
                    {
                        'name': field_.name,
                        'in': 'TODO',
                        'description': 'TODO',
                        'required': 'required' in field_.metadata and field_.metadata['required'] is True,
                        'schema': {
                            'type': field_.type,
                        }
                    }
                    for field_ in list(filter(lambda f: not f.name.startswith('_'), fields(endpoint.service)))
                ]

    def _request_body(self, endpoint: ffd.HttpEndpoint):
        if not inspect.isclass(endpoint.service):
            return None

        if endpoint.method.lower() in ('post', 'put', 'patch'):
            return {
                'required': True,
                'content': {
                    'application/json': {'schema': {
                        '$ref': f'#/components/schemas/{self._add_schema(endpoint.service)}'}
                    }
                }
            }

    def _add_schema(self, cls: typing.Union[Type[ffd.ValueObject], Type[ffd.ApplicationService]]):
        try:
            if cls.__name__ in self._schemas:
                return cls.__name__
        except AttributeError:
            pass

        if issubclass(cls, ffd.ValueObject):
            return self._add_entity_schema(cls)
        elif issubclass(cls, ffd.ApplicationService):
            return self._add_service_body_schema(cls)

    def _add_service_body_schema(self, cls: Type[ffd.ApplicationService]):
        props = {}
        signature = inspect.signature(cls.__call__)
        hints = typing.get_type_hints(cls.__call__)
        for name, param in signature.parameters.items():
            if name == 'self' or param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            try:
                type_ = hints[name]
            except KeyError:
                type_ = str
            self._handle_type(name, type_, props)

        self._spec.components.schema(cls.__name__, {'properties': props})
        self._schemas.append(cls.__name__)
        return cls.__name__

    def _add_entity_schema(self, cls: Type[ffd.ValueObject]):
        props = {}
        hints = typing.get_type_hints(cls)
        if not is_dataclass(cls):
            return None
        for field_ in fields(cls):
            if field_.name.startswith('_'):
                continue
            type_ = hints[field_.name]
            self._handle_type(field_.name, type_, props)

        self._spec.components.schema(cls.__name__, {'properties': props})
        self._schemas.append(cls.__name__)
        return cls.__name__

    def _handle_type(self, name: str, type_: type, props: dict):
        if inspect.isclass(type_) and issubclass(type_, (ffd.Entity, ffd.ValueObject)):
            props[name] = {
                'type': {
                    'schema': {
                        '$ref': f'#/components/schemas/{self._add_schema(type_)}'
                    }
                }
            }
        elif ffd.is_type_hint(type_) and ffd.get_origin(type_) is typing.List:
            t = ffd.get_args(type_)[0]
            props[name] = {
                'type': 'array',
                'items': {
                    '$ref': f'#/components/schemas/{self._add_schema(t)}'
                }
            }
        elif ffd.is_type_hint(type_) and ffd.get_origin(type_) is typing.Union:
            args = ffd.get_args(type_)
            if args[1] is None:
                props[name] = self._map_type(args[0])
                props[name].update({'required': False})
        elif ffd.is_type_hint(type_) and ffd.get_origin(type_) is typing.Dict:
            props[name] = {'type': 'object'}
        else:
            props[name] = self._map_type(type_)

    def _map_type(self, type_: type):
        if type_ is str or type_ == 'str':
            return {'type': 'string'}
        elif type_ is int or type_ == 'int':
            return {'type': 'integer'}
        elif type_ is float or type_ == 'float':
            return {'type': 'number'}
        elif type_ is bool or type_ == 'bool':
            return {'type': 'boolean'}
        elif type_ is list or type_ == 'list':
            return {'type': 'array'}
        elif type_ is dict or type_ == 'dict':
            return {'type': 'object'}
        elif type_ is datetime or type_ == 'datetime':
            return {'type': 'string', 'format': 'date-time'}
        elif type_ is date or type_ == 'date':
            return {'type': 'string', 'format': 'date'}

        raise Exception(f"Don't know how to handle type: {type_}")
