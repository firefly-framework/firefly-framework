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
import inspect

import firefly.domain as ffd
import firefly.infrastructure as ffi
import inflection


@ffd.on(ffd.DomainEntitiesLoaded)
class ConfigureStorage(ffd.ApplicationService):
    _config: ffd.Configuration = None
    _context_map: ffd.ContextMap = None
    _registry: ffd.Registry = None
    _serializer: ffd.Serializer = None
    _rdb_storage_interface_registry: ffi.RdbStorageInterfaceRegistry = None

    def __init__(self):
        self._connection_factories = {}
        self._repository_factories = {}

    def __call__(self, **kwargs):
        self._load_factories()
        connections = {}
        factories = {}

        for context in self._context_map.contexts:
            storage = context.config.get('storage', {})
            if 'services' in storage:
                for name, config in storage.get('services').items():
                    config = config or {}
                    if name not in self._connection_factories and config.get('type') not in self._connection_factories:
                        raise ffd.ConfigurationError(f"No ConnectionFactory configured for '{name}'")
                    key = name if name in self._connection_factories else config.get('type')
                    connections[name] = context.container.build(self._connection_factories[key])(
                        **(config.get('connection') or {})
                    )

        for context in self._context_map.contexts:
            storage = context.config.get('storage', {})
            if 'services' in storage:
                for name, config in storage.get('services').items():
                    config = config or {}
                    if name not in self._repository_factories and config.get('type') not in self._repository_factories:
                        raise ffd.ConfigurationError(f"No RepositoryFactory configured for '{name}'")
                    key = name if name in self._repository_factories else config.get('type')
                    factory = context.container.autowire(self._repository_factories[key])
                    try:
                        factories[name] = factory(connections[name], **(config.get('repository') or {}))
                    except TypeError as e:
                        if '__init__() takes exactly one argument' in str(e):
                            raise ffd.FrameworkError(f"{factory.__name__}.__init__() must take a connection as "
                                                     f"the first argument")
                        raise e

        for context in self._context_map.contexts:
            if context.name == 'firefly':
                continue
            storage = context.config.get('storage', {})
            registered_aggregates = []
            if 'aggregates' in storage:
                for entity, service in storage.get('aggregates').items():
                    if not entity.startswith(context.name):
                        entity = f'{context.name}.{entity}'
                    entity = ffd.load_class(entity)
                    registered_aggregates.append(entity)
                    self._registry.register_factory(entity, factories[service])
            if 'default' in storage:
                for entity in context.entities:
                    if issubclass(entity, ffd.AggregateRoot) and entity is not ffd.AggregateRoot \
                            and entity not in registered_aggregates:
                        self._registry.register_factory(entity, factories[storage.get('default')])

        # TODO Get persistence working in these core services.
        # self._registry(ffd.ContextMap).add(self._context_map)

        self.dispatch(ffd.StorageConfigured())

    def _load_factories(self):
        for context in self._context_map.contexts:
            module_name = context.config.get('infrastructure_module', '{}.infrastructure')
            try:
                module = importlib.import_module(module_name.format(context.name))
            except ModuleNotFoundError:
                continue

            for k, v in module.__dict__.items():
                if not inspect.isclass(v):
                    continue
                if issubclass(v, ffd.ConnectionFactory):
                    self._connection_factories[inflection.underscore(v.__name__.replace('ConnectionFactory', ''))] = v
                elif issubclass(v, ffd.RepositoryFactory):
                    self._repository_factories[inflection.underscore(v.__name__.replace('RepositoryFactory', ''))] = v
                elif issubclass(v, ffi.RdbStorageInterface) and v is not ffi.RdbStorageInterface:
                    name = inflection.underscore(k.replace('StorageInterface', ''))
                    self._rdb_storage_interface_registry.add(name, v)
