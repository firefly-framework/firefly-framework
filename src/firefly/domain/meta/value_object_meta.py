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

# __pragma__('skip')
from abc import ABCMeta
from dataclasses import dataclass
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABCMeta, ABC, dataclass
?"""
# __pragma__ ('noecom')

import firefly.domain as ffd


class ValueObjectMeta(ABCMeta):
    def __new__(mcs, name, bases, dct, **kwargs):
        # __pragma__('skip')
        ret = super().__new__(mcs, name, bases, dct)
        # __pragma__('noskip')
        # __pragma__ ('ecom')
        """?
        ret = type.__new__(type, name, bases, dct)
        ?"""
        # __pragma__ ('noecom')
        ret = dataclass(ret, eq=False)

        return ret
