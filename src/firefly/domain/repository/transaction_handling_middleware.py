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

from typing import Callable

import firefly.domain as ffd

from .registry import Registry
from ..service.logging.logger import LoggerAware
from ..service.messaging.middleware import Middleware


class TransactionHandlingMiddleware(Middleware, LoggerAware):
    _registry: Registry = None

    def __init__(self):
        self._level = 0

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        try:
            if self._level == 0:
                self.debug('Level 0 - Resetting repositories')
                self.debug(message)
                self._reset()
            self._level += 1
            self.debug('Level incremented: %d', self._level)
            ret = next_(message)
            self._level -= 1
            self.debug('Level decremented: %d', self._level)
            if self._level == 0:
                self.debug('Level 0 - Committing changes')
                self._commit()
            return ret
        except Exception as e:
            self.error(str(e))
            self.debug('Caught an exception during transaction')
            self._level -= 1
            self.debug('Level decremented: %d', self._level)
            if self._level == 0:
                self.debug('Level 0 - Resetting repositories')
                self._reset()
            raise e

    def _reset(self):
        for repository in self._registry.get_repositories():
            repository.reset()

    def _commit(self):
        for repository in self._registry.get_repositories():
            self.debug('Committing repository %s', repository)
            repository.commit()
