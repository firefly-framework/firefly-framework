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

from pprint import pprint
from typing import Optional

import firefly.domain as ffd


CATEGORIES = ('read', 'write', 'admin')


class AuthorizeScope(ffd.Handler, ffd.LoggerAware):
    def handle(self, message: ffd.Message) -> Optional[bool]:
        ret = True
        if message.headers.get('secured'):
            ret = False
            user_scopes = message.headers.get('decoded_token', {}).get('scopes') or []
            scopes = message.headers.get('scopes', [])
            self.info('Required scopes: %s', scopes)
            self.info('User scopes: %s', user_scopes)
            if len(scopes) > 0:
                for scope in message.headers.get('scopes', []):
                    for user_scope in user_scopes:
                        if self._has_grant(scope, user_scope):
                            self.info('User has grant... returning True')
                            return True
            else:
                self.info('No scopes required... returning True')
                ret = True

        self.info('Returning %s', str(ret))

        return ret

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
