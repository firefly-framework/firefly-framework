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

import firefly.infrastructure as ffi
import pytest
import firefly.domain as ffd


@pytest.mark.skip
def test_endpoint_scopes_are_updated(config):
    config['contexts']['todo']['is_extension'] = True
    config['contexts']['new_todo'] = {
        'extends': 'todo',
    }
    from firefly.application import Container
    Container.configuration = lambda self: ffi.MemoryConfigurationFactory()(config)

    c = Container()
    c.kernel.boot()

    for endpoint in c.context_map.get_context('new_todo').endpoints:
        if isinstance(endpoint, ffd.HttpEndpoint):
            for scope in endpoint.scopes:
                assert scope.startswith('new_todo.')

    endpoint = c.rest_router.match('/new-todo/todo-lists/abc123', 'get')
    for scope in endpoint[0].scopes:
        assert scope.startswith('new_todo.')
