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

from sqlalchemy import MetaData
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

import firefly.domain as ffd
from firefly.domain.service.core.chalice_application import STATUS_CODES, ACCESS_CONTROL_HEADERS, \
    chalice_response


@ffd.middleware()
class BeginTransaction(ffd.Middleware):
    _session: Session = None
    _meta: MetaData = None

    def __call__(self, event, get_response: Callable) -> Any:
        try:
            if self._session:
                self._session.begin()
        except InvalidRequestError as e:
            if 'A transaction is already begun on this Session' not in str(e):
                raise e

        try:
            ret = get_response(event)
            if self._session:
                self._session.commit()
        except ffd.ApiError as e:
            self._rollback()
            if e.__class__.__name__ in STATUS_CODES:
                return chalice_response({
                    'status_code': STATUS_CODES[e.__class__.__name__],
                    'headers': ACCESS_CONTROL_HEADERS,
                    'body': None,
                })
            raise e
        except ffd.UnauthenticatedError:
            self._rollback()
            return chalice_response({
                'status_code': 403,
                'headers': ACCESS_CONTROL_HEADERS,
                'body': None,
            })
        except Exception:
            self._rollback()
            raise

        return ret

    def _rollback(self):
        if self._session:
            self._session.rollback()
