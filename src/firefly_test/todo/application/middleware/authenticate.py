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
from typing import Optional

import firefly as ff


@ff.authenticator()
class Authenticate(ff.Handler):
    def handle(self, message: ff.Message) -> Optional[bool]:
        if hasattr(message, 'fail_authentication'):
            raise ff.UnauthenticatedError()

        if hasattr(message, 'scopes'):
            message.headers['decoded_token'] = {
                'scopes': json.loads(message.scopes),
            }
        return True


@ff.authenticator()
class Authenticate2(ff.Handler):
    def handle(self, message: ff.Message) -> Optional[bool]:
        if hasattr(message, 'fail_authentication2'):
            raise ff.UnauthenticatedError()

        return True
