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

from typing import List, Optional, Union

import firefly.domain as ffd

from ..messaging.system_bus import SystemBusAware
from ...entity.core.user import User

CATEGORIES = ('read', 'write', 'admin')


class Kernel(SystemBusAware):
    user: Optional[User] = None
    required_scopes: Optional[List[str]] = None
    http_request: Optional[dict] = None
    secured: Optional[bool] = None

    def reset(self):
        self.user = None
        self.required_scopes = None
        self.http_request = None
        self.secured = None

    @property
    def is_authorized(self):
        if self.required_scopes is None or len(self.required_scopes) == 0:
            return True  # No required scopes, return True

        if self.user is None:
            return self.secured is False

        if len(self.user.scopes) > 0:
            for scope in self.required_scopes:
                for user_scope in self.user.scopes:
                    if self._has_grant(scope, user_scope):
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

    def has_tenant(self):
        return self.user is not None and self.user.tenant is not None

    def reject_missing_tenant(self):
        if not self.has_tenant():
            raise ffd.Unauthorized()

    def reject_if_missing(self, scopes: Union[str, List[str]]):
        if self.user is None:
            raise ffd.Unauthorized()

        if isinstance(scopes, str):
            scopes = [scopes]
        for my_scope in self.user.scopes:
            reject = True
            for scope in scopes:
                if self._has_grant(my_scope, scope):
                    reject = False
                    break
            if reject:
                raise ffd.Unauthorized()

    def boot(self):
        self.invoke(ffd.LoadContainers())
