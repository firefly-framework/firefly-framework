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

from urllib.parse import parse_qs

import firefly.domain as ffd


class TranslateHttpEvent:
    _router: ffd.RestRouter = None
    _context: str = None

    def __call__(self, event: dict) -> dict:
        if 'requestContext' not in event or 'http' not in event.get('requestContext', {}):
            return event

        method = event['requestContext']['http']['method']
        path = event['rawPath']
        if path.startswith('/api'):
            path = path.replace('/api/', '/')

        endpoint, params = self._router.match(path, method)

        return {
            'resource': path,
            'path': path,
            'httpMethod': method,
            'requestContext': {
                'resourcePath': endpoint.route if endpoint is not None else event.get('rawPath'),
                'httpMethod': method,
                'path': path,
            },
            'headers': event.get('headers'),
            'queryStringParameters': event.get('queryStringParameters'),
            'pathParameters': params,
            'stageVariables': None,
            'body': event.get('body'),
            'isBase64Encoded': event.get('isBase64Encoded'),
            'multiValueQueryStringParameters': parse_qs(event.get('rawQueryString')),
        }
