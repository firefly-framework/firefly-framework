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

import inspect
from typing import Union, List

import firefly as ff
import firefly.domain.error as error


class On:
    def __call__(self, event: Union[str, type, List[Union[str, type]]]):
        def on_wrapper(cls):
            try:
                cls.add_event(event)
            except AttributeError:
                if inspect.isfunction(cls):
                    ff.add_event(cls, event)
                else:
                    raise error.FrameworkError('@on used on invalid target')
            return cls

        return on_wrapper


on = On()
