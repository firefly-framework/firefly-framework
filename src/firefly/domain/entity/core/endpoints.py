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

from dataclasses import field
from typing import Type, List, Union

import firefly.domain as ffd
from pydantic.dataclasses import dataclass

CATEGORIES = ('read', 'write', 'admin')


@dataclass
class HttpEndpoint:
    route: str
    service: type = None
    message: Union[Type[ffd.Message], str] = None
    method: str = 'GET'
    query_params: dict = field(default_factory=lambda: {})
    secured: bool = True
    scopes: List[str] = field(default_factory=lambda: [])
    tags: List[str] = field(default_factory=lambda: [])

    def __eq__(self, other):
        return isinstance(other, HttpEndpoint) and self.route == other.route and self.method == other.method

    def validate_scope(self, scope: str):
        self.info('Calling is_authorized')
        if self.scopes is None or len(self.scopes) == 0:
            return True  # No required scopes, return True

        for s in self.scopes:
            if self._has_grant(s, scope):
                return True

        return False

    @staticmethod
    def _has_grant(scope: str, user_scope: str):
        parts = scope.lower().split('.')
        user = user_scope.lower().split('.')

        for i, part in enumerate(parts):
            if i >= len(user):
                return False

            if user[i] == 'admin':
                return True

            if part not in CATEGORIES and part != user[i]:
                return False

            if part in CATEGORIES:
                if user[i] not in CATEGORIES:
                    return False
                if part == 'admin':
                    return False
                if part == 'write':
                    return user[i] == 'write'
                if part == 'read':
                    return user[i] in ('read', 'write')

        return True
