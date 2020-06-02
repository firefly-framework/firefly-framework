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

from typing import Callable, Dict

from firefly import domain as ffd
from firefly.domain.service.content_negotiation.content_converter import ContentConverter
from firefly.domain.service.logging import LoggerAware
from firefly.domain.service.messaging.middleware import Middleware


class ContentNegotiator(Middleware, LoggerAware):
    _converters: Dict[str, ContentConverter] = None

    def __init__(self, converters: Dict[str, ContentConverter], logger: ffd.Logger):
        self._converters = converters
        self._logger = logger

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        accept = None
        try:
            headers = message.headers['http_request']['headers']
            for k, v in headers.items():
                if k.lower() == 'accept':
                    accept = v
                    break
        except (KeyError, AttributeError):
            pass

        response = next_(message)

        if accept is None:
            return response

        mimes = accept.split(',')
        ordered_mimes = []
        for mime_type in mimes:
            if ';' in mime_type:
                self.info(mime_type)
                parts = mime_type.split(';')
                mime_type = parts.pop(0)
                found = False
                for part in parts:
                    if part.startswith('q='):
                        ordered_mimes.append((mime_type, part.split('=')[1]))
                if not found:
                    ordered_mimes.append((mime_type, '1.0'))
            else:
                ordered_mimes.append((mime_type, '1.0'))
        ordered_mimes.sort(key=lambda i: i[1], reverse=True)

        for mime_type in ordered_mimes:
            mime_type = str(mime_type[0]).strip()
            if mime_type in self._converters and self._converters[mime_type].can_convert(message, response):
                return self._converters[mime_type].convert(message, response)

        return response
