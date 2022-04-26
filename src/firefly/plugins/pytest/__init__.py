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

import os

from sqlalchemy.orm import Session, close_all_sessions

import firefly as ff
import firefly.infrastructure as ffi
import pytest
from chalice.test import TestHTTPClient
from firefly.infrastructure.service.messaging.chalice_message_transport import ChaliceMessageTransport

os.environ['FF_ENVIRONMENT'] = 'test'


@pytest.fixture(scope="session")
def config():
    raise Exception('You must provide a config fixture.')


@pytest.fixture(scope="session")
def kernel(config) -> ff.Kernel:
    ff.Kernel.configuration = lambda self: ffi.MemoryConfigurationFactory()(config)
    kernel: ff.Kernel = ff.Kernel().boot()
    kernel.register_object('message_transport', ChaliceMessageTransport)

    kernel.sqlalchemy_metadata.drop_all(checkfirst=True)
    kernel.sqlalchemy_metadata.create_all(checkfirst=True)

    return kernel


@pytest.fixture(scope="session")
def client(kernel) -> TestHTTPClient:
    return kernel.get_application().get_test_client().http


@pytest.fixture(scope="session")
def system_bus(kernel):
    return kernel.system_bus


@pytest.fixture(scope="function")
def registry(kernel):
    kernel.sqlalchemy_session.commit()
    kernel.sqlalchemy_session.begin_nested()

    yield kernel.registry

    kernel.sqlalchemy_session.rollback()
    for entity in kernel.get_aggregates():
        kernel.registry(entity).reset()


@pytest.fixture(scope="session")
def serializer(kernel):
    return kernel.serializer


@pytest.fixture(scope="session")
def map_entities(kernel):
    return kernel.map_entities


@pytest.fixture(scope="session")
def message_factory(kernel):
    return kernel.message_factory
