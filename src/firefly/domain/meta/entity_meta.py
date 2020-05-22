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
from dataclasses import dataclass, fields

import firefly as ff
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABCMeta, ABC, dataclass, fields
?"""
# __pragma__ ('noecom')

import firefly.domain as ffd


class EntityMeta(ABCMeta):
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

        # __pragma__('skip')
        is_aggregate = False
        for c in bases:
            # We can't import AggregateRoot for a proper issubclass check without getting a circular reference.
            if 'AggregateRoot' in str(c):
                is_aggregate = True
                break

        if is_aggregate:
            if 'create_on' in kwargs:
                ret._create_on = kwargs['create_on']
            if 'delete_on' in kwargs:
                ret._delete_on = kwargs['delete_on']
            if 'update_on' in kwargs:
                ret._update_on = kwargs['update_on']
            if 'sync_with' in kwargs:
                ret._create_on = f"{kwargs['sync_with']}Created"
                ret._delete_on = f"{kwargs['sync_with']}Deleted"
                ret._update_on = f"{kwargs['sync_with']}Updated"
        # __pragma__('noskip')

        return ret

    def __init__(cls, name, bases, dct, **kwargs):
        super().__init__(name, bases, dct)
        cls._c = None

    # __pragma__('skip')
    # noinspection PyDataclass
    @property
    def c(cls):
        if cls._c is None:
            from firefly.domain.repository.search_criteria import AttrFactory
            cls._c = AttrFactory([x.name for x in fields(cls)])
        return cls._c
    # __pragma__('noskip')
