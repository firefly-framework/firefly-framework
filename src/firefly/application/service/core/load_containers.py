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

import importlib

import firefly.domain as ffd
import firefly_di as di


class LoadContainers(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _container: di.Container = None

    def __call__(self):
        self.debug('LoadContainers called')
        for context in self._context_map.contexts:
            self.debug(f'Checking context "{context.name}"')
            if context.name == 'firefly':
                context.container = self._container
            else:
                context.container = self._load_module(context.name, context.config)
                self.debug(f'Loaded container: {context.container}')
                self._container.register_container(context.container)
            self.dispatch(ffd.ContainerInitialized(context=context.name))

        self.debug('All containers are built. Looping through again to link them all together.')
        for context in self._context_map.contexts:
            for name, config in (context.config.get('extensions', {}) or {}).items():
                self.debug(f'Registering {name} container with {context.name}')
                context.container.register_container(self._context_map.get_context(name).container)
            self.debug('Registering root container')
            context.container.register_container(self._container)

        self.dispatch(ffd.ContainersLoaded())

    def _load_module(self, name: str, config: dict) -> di.Container:
        module_name = config.get('container_module', '{}.application')
        try:
            module = importlib.import_module(module_name.format(name))
            container_cls = getattr(module, config.get('container_name', 'Container'))
        except (ModuleNotFoundError, AttributeError):
            class EmptyContainer(di.Container):
                pass
            container_cls = EmptyContainer

        container = container_cls()

        return container
