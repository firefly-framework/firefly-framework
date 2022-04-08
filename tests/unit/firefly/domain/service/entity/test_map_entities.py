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

from pprint import pprint

import firefly_test.todo.domain as todo
import pytest
from firefly import ParseRelationships
from firefly.domain.service.entity.map_entities import MapEntities
from firefly.infrastructure import EngineFactory, PythonLogger
from sqlalchemy import MetaData, Column, Table, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import InstrumentedAttribute, class_mapper


def test_one_to_one(sut, metadata):
    sut([todo.User, todo.Settings])




@pytest.fixture()
def sut(engine, metadata):
    ret = MapEntities()
    ret._logger = PythonLogger()

    ret._parse_relationships = ParseRelationships()
    ret._engine = engine
    ret._metadata = metadata

    return ret


@pytest.fixture()
def engine():
    engine_factory = EngineFactory()
    engine_factory._db_name = 'firefly'
    engine_factory._db_user = 'firefly'
    engine_factory._db_password = 'Abcd1234!'
    engine_factory._db_host = 'localhost'
    engine_factory._db_type = 'postgresql'
    engine_factory._db_port = '5432'

    return engine_factory(echo=True)


@pytest.fixture()
def metadata(engine):
    return MetaData(bind=engine)
