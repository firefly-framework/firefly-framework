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

from typing import Union, List

from .framework_annotation import FrameworkAnnotation


class On(FrameworkAnnotation):
    CRUD_ACTIONS = ['create', 'retrieve', 'update', 'delete']

    def name(self) -> str:
        return '__ff_listener'

    def __call__(self, event: Union[str, type, List[Union[str, type]]], action: str = None):
        kwargs = {'event': event}
        if action in self.CRUD_ACTIONS:
            kwargs['crud'] = action
        return super()._attach_annotation(**kwargs)


on = On()
