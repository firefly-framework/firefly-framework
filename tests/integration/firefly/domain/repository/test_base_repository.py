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

from typing import Callable, Optional, List, Union, Tuple

import firefly as ff
from firefly import domain as ffd
from firefly.domain.repository.repository import T


class Widget(ff.AggregateRoot):
    id: str = ff.id_()
    name: str = ff.optional()
    value: int = ff.optional()


class WidgetRepository(ff.Repository[Widget]):
    def __init__(self, foos):
        self._foos = foos
        self._index = 0

    def append(self, entity: T, **kwargs):
        pass

    def remove(self, entity: T, **kwargs):
        pass

    def find(self, exp: Union[str, Callable], **kwargs) -> Optional[T]:
        pass

    def filter(self, cb: Callable, **kwargs) -> List[T]:
        criteria = self._get_search_criteria(cb)
        return list(filter(lambda i: criteria.matches(i), self._foos))

    def reduce(self, cb: Callable) -> Optional[T]:
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._foos):
            self._index = 0
            raise StopIteration()
        self._index += 1
        return self._foos[self._index - 1]

    def __len__(self):
        return len(self._foos)

    def __getitem__(self, item):
        return self._foos[item]

    def commit(self):
        pass

    def execute_ddl(self):
        pass

    def sort(self, cb: Union[Callable, Tuple[Union[str, Tuple[str, bool]]]]):
        pass


def test_search_criteria():
    widgets = WidgetRepository([
        Widget(name='widget1', value=1),
        Widget(name='widget2', value=2),
        Widget(name='widget3', value=3),
        Widget(name='WIDGET4', value=4),
    ])

    assert len(widgets.filter(lambda w: w.name == 'widget2')) == 1
    assert len(widgets.filter(lambda w: w.name.startswith('widget'))) == 3
    assert len(widgets.filter(lambda w: w.name.startswith('widget') and w.value == 2)) == 1
    assert len(widgets.filter(lambda w: w.name.lower().startswith('widget'))) == 4
    assert len(widgets.filter(lambda w: w.name.lower() == 'widget4')) == 1

    lst = []
    for widget in widgets:
        lst.append(widget)
    assert len(lst) == 4
