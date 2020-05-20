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

import importlib
import os
from dataclasses import is_dataclass
from typing import Any

import firefly.domain as ffd
from firefly import Message
from jinja2 import Environment, TemplateNotFound, BaseLoader, select_autoescape


class HtmlConverter(ffd.ContentConverter):
    def __init__(self, config: ffd.Configuration):
        self._environments = {}

        for name, context in config.contexts.items():
            context = context or {}
            self._environments[name] = Environment(
                loader=TemplateLoader(name, context),
                autoescape=select_autoescape(
                    context.get('output', {}).get('autoescape', ['html', 'xml'])
                )
            )

    def can_convert(self, request: Message, response: Any):
        try:
            self._get_template(request)
            return True
        except (KeyError, TemplateNotFound):
            return False

    def convert(self, request: Message, response: Any):
        template = self._get_template(request)

        body = None
        if isinstance(response, dict) and not is_dataclass(response):
            body = template.render(**response)
        elif isinstance(response, Message):
            body = template.render(**response.to_dict())

        if body is not None:
            response = ffd.HttpResponse(body=body, headers={
                'Content-Type': 'text/html',
            })

        return response

    def _get_template(self, message: Message):
        request = message.headers['http_request']
        return self._environments[message.get_context()]\
            .get_template(f"{request['path']}.{request['method'].lower()}.html")


class TemplateLoader(BaseLoader):
    def __init__(self, context: str, config: dict):
        self._paths = []
        try:
            m = importlib.import_module('templates')
            for path in m.__path__:
                self._paths.append(path)
        except ModuleNotFoundError:
            pass

        module_name = config.get('template_module', f'{context}.ui.templates')
        try:
            m = importlib.import_module(module_name)
            for path in m.__path__:
                self._paths.append(path)
        except ModuleNotFoundError:
            pass

    def get_source(self, environment, template):
        for path in self._paths:
            full_path = os.path.join(path, str(template).lstrip('/'))
            if not os.path.exists(full_path):
                raise TemplateNotFound(template)
            mtime = os.path.getmtime(full_path)
            with open(full_path, 'r') as fp:
                source = fp.read()
            return source, full_path, lambda: mtime == os.path.getmtime(full_path)

        raise TemplateNotFound(template)
