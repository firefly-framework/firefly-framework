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

from typing import Dict, Optional, Tuple

import firefly.domain as ffd
from routes import Mapper


class RoutesRestRouter(ffd.RestRouter):
    def __init__(self):
        self._maps: Dict[str, Mapper] = {}

    def register(self, route: str, action: str, method: str = 'get'):
        if method.lower() not in self._maps:
            self._maps[method.lower()] = Mapper()
        self._maps[method.lower()].connect(route, action=action)

    def match(self, route: str, method: str = 'get') -> Optional[Tuple[str, dict]]:
        result = self._maps[method.lower()].match(route)
        if result is None and 'any' in self._maps:
            result = self._maps['any'].match(route)

        if result is None:
            return None

        action = result['action']
        del result['action']

        return action, result
