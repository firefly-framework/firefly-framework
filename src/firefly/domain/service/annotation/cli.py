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

from typing import Union, Type, List

import firefly.domain as ffd

NAME: str = '__ff_cli'


def cli(target: Union[str, Type[ffd.ApplicationService]] = None, name: str = None, description: str = None,
        alias: dict = None, help_: dict = None, middleware: List[ffd.Middleware] = None, app_name: str = None):
    kwargs = locals()

    def wrapper(cls):
        if kwargs['name'] is None:
            kwargs['name'] = cls.__name__
        setattr(cls, NAME, kwargs)
        cls.__ff_port = True
        return cls

    return wrapper
