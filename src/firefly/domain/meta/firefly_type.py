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

import typing

from firefly.domain.meta.context_aware import ContextAware

# __pragma__('skip')
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABC
?"""
# __pragma__ ('noecom')


class FireflyType(ContextAware, ABC):
    _context: str = None

    def __str__(self):
        try:
            context = self.__class__._context
            if context is None:
                context = self._context
        except AttributeError:
            context = self._context

        return f'{context}.{self.__class__.__name__}' \
            if context is not None else self.__class__.__name__

    def __repr__(self):
        return str(self)

    def is_this(self, this_: typing.Any):
        if isinstance(this_, str) and this_ == str(self):
            return True
        try:
            return isinstance(self, this_) and self.__class__.__name__ == this_.__name__
        except TypeError:
            return False

    def get_context(self):
        return self._context
