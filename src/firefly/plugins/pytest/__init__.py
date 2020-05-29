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

import pytest
import firefly as ff
import firefly.infrastructure as ffi


@pytest.fixture(scope="session")
def config():
    raise Exception('You must provide a config fixture.')


@pytest.fixture(scope="session")
def container(config):
    from firefly.application import Container
    Container.configuration = lambda self: ffi.MemoryConfigurationFactory()(config)

    c = Container()
    # c.registry.set_default_factory(ffi.MemoryRepositoryFactory())

    c.kernel.boot()

    return c


@pytest.fixture(scope="session")
def kernel(container) -> ff.Kernel:
    return container.kernel


@pytest.fixture(scope="session")
def context_map(container) -> ff.ContextMap:
    return container.context_map


@pytest.fixture(scope="session")
def system_bus(container) -> ff.SystemBus:
    return container.system_bus


@pytest.fixture(scope="session")
def message_factory(container) -> ff.MessageFactory:
    return container.message_factory


@pytest.fixture(scope="session")
def serializer(container):
    return container.serializer


@pytest.fixture(scope="function")
def registry(container, request) -> ff.Registry:
    registry = container.registry

    def teardown():
        for context in container.context_map.contexts:
            for entity in context.entities:
                if issubclass(entity, ff.AggregateRoot) and entity is not ff.AggregateRoot:
                    try:
                        for e in registry(entity):
                            registry(entity).remove(e)
                    except ff.FrameworkError:
                        pass
            try:
                context.container.db_api_interface_registry.disconnect_all()
            except AttributeError:
                pass
    request.addfinalizer(teardown)
    # registry.clear_cache()
    return registry


@pytest.fixture(scope="function")
async def client(container, system_bus, aiohttp_client):
    deployment = ff.Deployment(project='Test', environment='testing', provider='default')
    system_bus.dispatch('firefly.DeploymentCreated', {'deployment': deployment})
    agent = container.agent_factory('default')
    agent(deployment, start_server=False)
    container.web_server.initialize()
    return await aiohttp_client(container.web_server.app)
