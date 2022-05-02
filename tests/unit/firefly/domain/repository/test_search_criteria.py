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
import json
from datetime import datetime, date

import pytest
import firefly as ff
from firefly.domain.service.serialization.serializer import JSONEncoder as FireflyEncoder
from dateparser import parse


def test_datetime(spy):
    def criteria(x):
        return x.my_date == datetime(year=1990, month=1, day=1)
    c = criteria(spy)

    assert isinstance(c.rhv, datetime)
    j = json.dumps(c.to_dict(), cls=FireflyEncoder)
    print()
    print(j)
    print(json.loads(j))
    c = ff.SearchCriteria.from_dict(json.loads(j))
    print(c.to_dict())
    print('---')
    assert isinstance(c.rhv, datetime)


def test_date(spy):
    def criteria(x):
        return x.my_date == date(year=1990, month=1, day=1)
    c = criteria(spy)
    assert isinstance(c.rhv, date)
    j = json.dumps(c.to_dict(), cls=FireflyEncoder)
    c = ff.SearchCriteria.from_dict(json.loads(j))
    assert isinstance(c.rhv, date)


def test_is_not_none(spy):
    def criteria(x):
        return x.null_var.is_not_none()
    c = criteria(spy)
    assert 'null_var is not null' in c.to_sql()[0]


@pytest.fixture()
def spy():
    return ff.EntityAttributeSpy()
