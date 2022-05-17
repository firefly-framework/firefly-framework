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
import os
import re
from typing import List, Any

import firefly.domain.constants as const
import firefly.domain.error as error
import inflection
from firefly import domain as ffd
from firefly.domain.entity.core.endpoints import HttpEndpoint

function_name = re.compile(r'.*function\s([^\.]+)\..*')


class Rest(ffd.ConfigurationAnnotation):
    def __call__(self, route: str, method: str = 'GET', generates: type = None,
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
                query_params=query_params or {},
                service=cls,
                secured=secured,
                scopes=scopes or [],
                tags=tags or []
            )

            try:
                if hasattr(cls, const.HTTP_ENDPOINTS):
                    getattr(cls, const.HTTP_ENDPOINTS).append(endpoint)
                else:
                    setattr(cls, const.HTTP_ENDPOINTS, [endpoint])
            except AttributeError as e:
                raise error.FrameworkError('@rest used on invalid target') from e

            return cls

        return on_wrapper

    @staticmethod
    def crud(exclude: list = None, config: dict = None, prefix: str = None):
        exclude = exclude or []
        config = config or {}

        def on_wrapper(cls):
            if not hasattr(cls, const.HTTP_ENDPOINTS):
                setattr(cls, const.HTTP_ENDPOINTS, [])
            context = os.environ.get('CONTEXT')
            base = inflection.pluralize(inflection.dasherize(inflection.underscore(cls.__name__)))
            if prefix is not None:
                base = f'{prefix.strip("/")}/{base}'

            service_prefix = f'{inflection.dasherize(os.environ.get("CONTEXT"))}/'
            if not base.startswith(service_prefix):
                base = f'{service_prefix.rstrip("/")}/{base.lstrip("/")}'

            if 'create' not in exclude:
                getattr(cls, const.HTTP_ENDPOINTS).append(HttpEndpoint(
                    route=f'/{base}',
                    method='post',
                    message=f'{context}.Create{cls.__name__}',
                    service=cls,
                    secured=config.get('create', {}).get('secured', True),
                    scopes=config.get('create', {}).get('scopes', [f'{context}.{cls.__name__}.write'])
                ))

            if 'update' not in exclude:
                getattr(cls, const.HTTP_ENDPOINTS).append(HttpEndpoint(
                    route=f'/{base}/{{{cls.id_name()}}}',
                    method='put',
                    message=f'{context}.Update{cls.__name__}',
                    service=cls,
                    secured=config.get('update', {}).get('secured', True),
                    scopes=config.get('update', {}).get('scopes', [f'{context}.{cls.__name__}.write'])
                ))

            if 'delete' not in exclude:
                getattr(cls, const.HTTP_ENDPOINTS).append(HttpEndpoint(
                    route=f'/{base}/{{{cls.id_name()}}}',
                    method='delete',
                    message=f'{context}.Delete{cls.__name__}',
                    service=cls,
                    secured=config.get('delete', {}).get('secured', True),
                    scopes=config.get('delete', {}).get('scopes', [f'{context}.{cls.__name__}.write'])
                ))

            if 'read' not in exclude:
                getattr(cls, const.HTTP_ENDPOINTS).append(HttpEndpoint(
                    route=f'/{base}',
                    method='get',
                    message=f'{context}.{inflection.pluralize(cls.__name__)}',
                    service=cls,
                    secured=config.get('read', {}).get('secured', True),
                    scopes=config.get('read', {}).get('scopes', [f'{context}.{cls.__name__}.read'])
                ))

                getattr(cls, const.HTTP_ENDPOINTS).append(HttpEndpoint(
                    route=f'/{base}/{{{cls.id_name()}}}',
                    method='get',
                    message=f'{context}.{inflection.pluralize(cls.__name__)}',
                    service=cls,
                    secured=config.get('read', {}).get('secured', True),
                    scopes=config.get('read', {}).get('scopes', [f'{context}.{cls.__name__}.read'])
                ))

            return cls

        return on_wrapper

    def configure(self, cls: Any, kernel: ffd.Kernel):
        pass


rest = Rest()
