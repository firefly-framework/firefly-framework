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
import re
from typing import List

import firefly as ff
import firefly.domain.error as error
import inflection
from firefly.domain.entity.core.http_endpoint import HttpEndpoint


function_name = re.compile(r'.*function\s([^\.]+)\..*')


class Rest:
    def __call__(self, route: str, method: str = 'GET', generates: ff.TypeOfMessage = None, gateway: str = None,
                 query_params: dict = None, secured: bool = True, scopes: List[str] = None, tags: List[str] = None,
                 **kwargs):
        def on_wrapper(cls):
            prefix = ''
            if inspect.isfunction(cls):
                parent = function_name.match(str(cls)).groups()[0]
                prefix = f'/{inflection.pluralize(inflection.dasherize(inflection.underscore(parent)))}/{{id}}'

            endpoint = HttpEndpoint(
                route=prefix + route,
                method=method,
                message=generates,
                gateway=gateway,
                query_params=query_params,
                service=cls,
                secured=secured,
                scopes=scopes or [],
                tags=tags or []
            )

            try:
                cls.add_endpoint(endpoint)
            except AttributeError:
                if inspect.isfunction(cls):
                    ff.add_endpoint(cls, endpoint)
                else:
                    raise error.FrameworkError('@rest used on invalid target')
            return cls

        return on_wrapper

    @staticmethod
    def crud(exclude: list = None, gateway: str = None, config: dict = None, prefix: str = None):
        exclude = exclude or []
        config = config or {}

        def on_wrapper(cls):
            context = cls.get_class_context()
            base = inflection.pluralize(inflection.dasherize(inflection.underscore(cls.__name__)))
            if prefix is not None:
                base = f'{prefix.strip("/")}/{base}'
            if 'create' not in exclude:
                cls.add_endpoint(HttpEndpoint(
                    route=f'/{base}',
                    method='post',
                    message=f'{context}.Create{cls.__name__}',
                    gateway=gateway,
                    service=cls,
                    secured=config.get('create', {}).get('secured', True),
                    scopes=config.get('create', {}).get('scopes', [f'{context}.{cls.__name__}.write'])
                ))

            if 'update' not in exclude:
                cls.add_endpoint(HttpEndpoint(
                    route=f'/{base}/{{{cls.id_name()}}}',
                    method='put',
                    message=f'{context}.Update{cls.__name__}',
                    gateway=gateway,
                    service=cls,
                    secured=config.get('update', {}).get('secured', True),
                    scopes=config.get('update', {}).get('scopes', [f'{context}.{cls.__name__}.write'])
                ))

            if 'delete' not in exclude:
                cls.add_endpoint(HttpEndpoint(
                    route=f'/{base}/{{{cls.id_name()}}}',
                    method='delete',
                    message=f'{context}.Delete{cls.__name__}',
                    gateway=gateway,
                    service=cls,
                    secured=config.get('delete', {}).get('secured', True),
                    scopes=config.get('delete', {}).get('scopes', [f'{context}.{cls.__name__}.write'])
                ))

            if 'read' not in exclude:
                cls.add_endpoint(HttpEndpoint(
                    route=f'/{base}',
                    method='get',
                    message=f'{context}.{inflection.pluralize(cls.__name__)}',
                    gateway=gateway,
                    service=cls,
                    secured=config.get('read', {}).get('secured', True),
                    scopes=config.get('read', {}).get('scopes', [f'{context}.{cls.__name__}.read'])
                ))

                cls.add_endpoint(HttpEndpoint(
                    route=f'/{base}/{{{cls.id_name()}}}',
                    method='get',
                    message=f'{context}.{inflection.pluralize(cls.__name__)}',
                    gateway=gateway,
                    service=cls,
                    secured=config.get('read', {}).get('secured', True),
                    scopes=config.get('read', {}).get('scopes', [f'{context}.{cls.__name__}.read'])
                ))

            return cls

        return on_wrapper


rest = Rest()
