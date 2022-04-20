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

from typing import Callable, Any

import firefly.domain as ffd
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session


@ffd.middleware()
class BeginTransaction(ffd.Middleware):
    _session: Session = None

    def __call__(self, event, get_response: Callable) -> Any:
        try:
            self._session.begin()
        except InvalidRequestError as e:
            if 'A transaction is already begun on this Session' not in str(e):
                raise e

        try:
            ret = get_response(event)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

        return ret