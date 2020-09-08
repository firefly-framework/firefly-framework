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

from dataclasses import dataclass
from datetime import datetime, date, timedelta

import firefly.domain as ffd
import pytest
from firefly.domain.entity.entity import Entity


def test_constructor(sut):
    with pytest.raises(TypeError, match="missing 1 required argument"):
        sut()

    sut(required_field='foo')


def test_load_dict_type_coercion(sut):
    dt = datetime.now() - timedelta(days=1)
    d = dt.date()
    data = {
        'now': dt.isoformat(),
        'today': d.isoformat(),
    }

    s = sut(required_field='foo')
    s.load_dict(data)

    assert isinstance(s.now, datetime)
    assert isinstance(s.today, date)


def test_default_values(sut):
    s = sut(required_field='foo')
    assert isinstance(s.now, datetime)
    assert isinstance(s.today, date)
    assert s.strings == []


@pytest.fixture()
def sut():
    class ConcreteEntity(Entity):
        id: str = ffd.id_()
        strings: str = ffd.list_()
        now: datetime = ffd.now()
        today: date = ffd.today()
        required_field: str = ffd.required()

    return ConcreteEntity
