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

from typing import Dict, Optional, Tuple, Union

import firefly.domain as ffd
from routes import Mapper


class RoutesRestRouter(ffd.RestRouter):
    def __init__(self):
        self._maps: Dict[str, Mapper] = {}
        self._cache = {}

    def register(self, route: str, endpoint: ffd.HttpEndpoint):
        if endpoint.method.lower() not in self._maps:
            self._maps[endpoint.method.lower()] = Mapper()
        self._maps[endpoint.method.lower()].connect(route, action=endpoint)
        self._cache[str(endpoint)] = endpoint

    def match(self, route: str, method: str = 'get') -> Union[Tuple[ffd.HttpEndpoint, dict], Tuple[None, None]]:
        result = None
        map_ = None
        if method.lower() in self._maps:
            map_ = self._maps[method.lower()]
        if result is None and 'any' in self._maps:
            map_ = self._maps['any']

        if map_:
            map_.matchlist.sort(key=lambda rr: rr.routepath)
            result = map_.match(route)

        if result is None:
            return None, None

        action = result['action']
        del result['action']

        return self._cache[action], result
