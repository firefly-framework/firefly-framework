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

import json
from json import JSONDecodeError

import firefly.application as ffa
import firefly.domain as ffd


@ffd.query_handler()
class DefaultHttpMiddleware(ffd.Middleware):
    def __call__(self, message: ffd.Message, next_: callable):
        response = next_(message)

        if message.headers.get('origin') == 'http':
            try:
                return ffd.HttpMessage(http_headers={'status_code': '200', 'content_negotiation-type': 'application/json'},
                                       body=json.dumps(response))
            except (JSONDecodeError, TypeError):
                return response

        return response


@ffd.http(cors=True)
class HttpApi:
    @ffd.http('/services', target=ffa.GetRegisteredContainerServices)
    def services(self):
        pass
