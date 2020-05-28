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
from typing import Type, List

import firefly.domain as ffd
import inflection
import typing


@ffd.cli('firefly generate api-spec')
class GenerateApiSpec(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None

    def __init__(self):
        self._schemas = []

    def __call__(self, **kwargs):
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
        if not inspect.isclass(endpoint.service) or not issubclass(endpoint.service, ffd.Entity):
            return None

        if endpoint.method.lower() == 'post':
            return {
                'required': True,
                'content': {
                    'application/json': {'schema': {
                        '$ref': f'#/components/schemas/{self._add_schema(endpoint.service)}'}
                    }
                }
            }

    def _add_schema(self, entity: typing.Union[Type[ffd.Entity], Type[ffd.ValueObject]]):
        if entity.__name__ in self._schemas:
            return entity.__name__
        props = {}
        hints = typing.get_type_hints(entity)
        if not is_dataclass(entity):
            return None
        for field_ in fields(entity):
            if field_.name.startswith('_'):
                continue
            type_ = hints[field_.name]

            if inspect.isclass(type_) and issubclass(type_, (ffd.Entity, ffd.ValueObject)):
                props[field_.name] = {
                    'type': {
                        'schema': {
                            '$ref': f'#/components/schemas/{self._add_schema(type_)}'
                        }
                    }
                }
            elif isinstance(type_, type(List)):
                t = type_.__args__[0]
                props[field_.name] = {
                    'type': 'array',
                    'items': {
                        '$ref': f'#/components/schemas/{self._add_schema(t)}'
                    }
                }
            else:
                props[field_.name] = {'type': str(field_.type)}

        self._spec.components.schema(entity.__name__, {'properties': props})
        self._schemas.append(entity.__name__)
        return entity.__name__
