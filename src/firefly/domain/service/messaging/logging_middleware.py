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

import os
from typing import Callable

import firefly.domain as ffd
from firefly.domain.service.logging.logger import LoggerAware
from firefly.domain.service.messaging.middleware import Middleware


class LoggingMiddleware(Middleware, LoggerAware):
    def __init__(self, message: str = None):
        self._message = message or 'Message added to bus: %s'

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        original_log_level = None
        if ('DEBUG' in os.environ and os.environ['DEBUG']) or ('debug' in message.headers and message.headers['debug']):
            original_log_level = self._logger.get_level()
            self._logger.set_level_to_debug()

        self.info(self._message, message)
        try:
            self.info('Message properties: %s', message.to_dict())
        except AttributeError:
            pass
        ret = next_(message)
        self.info('Response: %s', str(ret))

        if original_log_level is not None:
            self._logger.set_level(original_log_level)

        return ret
