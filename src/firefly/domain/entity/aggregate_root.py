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

import firefly as ff

# __pragma__('skip')
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')

"""?
from firefly.presentation.web.polyfills import ABC
?"""
# __pragma__ ('noecom')

from firefly.domain.entity.entity import Entity, hidden
from firefly.domain.meta.meta_aware import MetaAware


class AggregateRoot(Entity, MetaAware, ABC):
    # __pragma__('skip')
    _create_on: ff.TypeOfEvent = hidden()
    _delete_on: ff.TypeOfEvent = hidden()
    _update_on: ff.TypeOfEvent = hidden()

    @classmethod
    def get_create_on(cls):
        return cls._create_on

    @classmethod
    def get_delete_on(cls):
        return cls._delete_on

    @classmethod
    def get_update_on(cls):
        return cls._update_on
    # __pragma__('noskip')
