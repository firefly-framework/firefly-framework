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

from abc import ABCMeta
from dataclasses import dataclass

import firefly.domain as ffd


class MessageMeta(ABCMeta):
    def __new__(mcs, name, bases, dct, **kwargs):
        my_dict = dct.copy()

        if 'fields_' in kwargs and 'annotations_' in kwargs:
            for k, v in kwargs['fields_'].items():
                my_dict[k] = v
            if '__annotations__' in my_dict:
                my_dict['__annotations__'].update(kwargs['annotations_'])
            else:
                my_dict['__annotations__'] = kwargs['annotations_']

        ret = type.__new__(mcs, name, bases, my_dict)

        return dataclass(ret, eq=False, repr=False)

    def __instancecheck__(self, instance):
        if self is ffd.Message:
            return True
        return self in instance.__class__.__bases__
