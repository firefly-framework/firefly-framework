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
from typing import Callable, Any

from chalice import Response

import firefly.domain as ffd

ACCESS_CONTROL_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Authorization, Accept, Accept-Language, Content-Language, Content-Type, '
                                    'Content-Range',
    'Access-Control-Expose-Headers': '*',
}


@ffd.middleware()
class HandleEnvelope(ffd.Middleware):
    _serializer: ffd.Serializer = None

    def __call__(self, event, get_response: Callable) -> Any:
        response = get_response(event)
        ret = response

        if isinstance(response, ffd.Envelope):
            ret = {
                'status_code': 200,
                'headers': ACCESS_CONTROL_HEADERS,
                'body': response.unwrap(),
            }

            try:
                ret['body'] = self._serializer.serialize(ret['body'])
            except json.JSONDecodeError:
                pass

            range_ = response.get_range()
            if range_ is not None:
                ret['status_code'] = 206
                if range_['upper'] > range_['total']:
                    range_['upper'] = range_['total']
                ret['headers']['content-range'] = f'{range_["lower"]}-{range_["upper"]}/{range_["total"]}'
                if 'unit' in range_:
                    ret['headers']['content-range'] = f'{range_["unit"]} {ret["headers"]["content-range"]}'

            if 'location' in response.headers:
                ret['status_code'] = 303
                ret['headers']['location'] = response.headers['location']

        if isinstance(ret, dict) and 'status_code' in ret:
            return Response(**ret)

        return ret
