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
import typing


def get_arguments(c: callable, none_type_unions: bool = True) -> dict:
    ret = {}
    sig = dict(inspect.signature(c).parameters)

    for k, v in typing.get_type_hints(c).items():
        if k == 'return':
            continue

        if none_type_unions is False:
            try:
                if len(v.__args__) == 2 and ('NoneType' in str(v.__args__[0]) or 'NoneType' in str(v.__args__[1])):
                    v = v.__args__[0] if 'NoneType' in str(v.__args__[1]) else v.__args__[1]
            except AttributeError:
                pass

        ret[k] = {
            'type': v,
            'default': sig[k].default,
            'kind': sig[k].kind,
        }

    return ret
