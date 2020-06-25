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

from abc import ABC, abstractmethod
from typing import Optional

from ...meta.meta_aware import MetaAware


class Handler(MetaAware, ABC):
    @abstractmethod
    def handle(self, *args, **kwargs) -> Optional[bool]:
        pass


class ChainOfResponsibility(ABC):
    def __init__(self):
        self._handlers = []

    def handle(self, *args, **kwargs):
        if len(self._handlers) == 0:
            return

        ret = False
        for handler in self._handlers:
            if handler.handle(*args, **kwargs) is True:
                ret = True
                break
        return ret

    def add(self, handler: Handler):
        self._handlers.append(handler)

    def remove(self, handler: Handler):
        self._handlers.remove(handler)

    @property
    def handlers(self):
        return self._handlers
