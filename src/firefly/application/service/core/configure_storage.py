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

import firefly.domain as ffd
import firefly.infrastructure as ffi


@ffd.on(ffd.DomainEntitiesLoaded)
class ConfigureStorage(ffd.ApplicationService):
    _config: ffd.Configuration = None
    _context_map: ffd.ContextMap = None
    _registry: ffd.Registry = None
    _serializer: ffd.Serializer = None

    def __call__(self, context: str, **kwargs):
        context = self._context_map.get_context(context)
        config = context.config.get('storage')
        if config is None:
            return

        self._configure_connections(config.get('connections', {}), context)
        self._configure_repositories(config, context)

        self._registry(ffd.ContextMap).add(self._context_map)

        self.dispatch(ffd.StorageConfigured(context=context.name))

    def _configure_connections(self, config: dict, context: ffd.Context):
        container = context.container.__class__
        if not hasattr(container, '__annotations__'):
            container.__annotations__ = {}
        interface_registry = ffi.DbApiStorageInterfaceRegistry()
        container.db_api_interface_registry = lambda self: interface_registry
        container.__annotations__['db_api_interface_registry'] = ffi.DbApiStorageInterfaceRegistry
        context.container.clear_annotation_cache()

        for name, c in config.items():
            try:
                type_ = c['type']
            except KeyError:
                raise ffd.ConfigurationError(f'type is a required field for connection {name}')

            if type_ == 'db_api':
                interface_registry.add(name, self._build_storage_interface(name, c))

    def _build_storage_interface(self, name: str, config: dict):
        try:
            driver = config['driver']
        except KeyError:
            raise ffd.ConfigurationError(f'driver is required in db_api connection {name}')

        if driver == 'sqlite':
            return ffi.SqliteStorageInterface(name, config, self._serializer)

    def _configure_repositories(self, config: dict, context: ffd.Context):
        container = context.container.__class__
        container.db_api_object_repository_factory = ffi.DbApiObjectRepositoryFactory
        container.__annotations__['db_api_object_repository_factory'] = ffi.DbApiObjectRepositoryFactory
        factory: ffi.DbApiObjectRepositoryFactory = context.container.db_api_object_repository_factory
        context.container.clear_annotation_cache()

        types = {}
        for k, v in config.items():
            if k == 'connections':
                continue
            if k == 'default':
                if v == 'memory':
                    self._registry.set_default_factory(context.name, ffi.MemoryRepositoryFactory())
                else:
                    factory.set_default_storage_interface(v)
                    self._registry.set_default_factory(context.name, factory)
                continue
            if v not in types:
                types[v] = []
            types[v].append(ffd.load_class(f'{context.name}.{k}'))

        for interface_name, entity_types in types.items():
            for entity_type in entity_types:
                if interface_name == 'memory':
                    self._registry.register_factory(entity_type, ffi.MemoryRepositoryFactory())
                else:
                    factory.register_storage_interface(entity_type, interface_name)
                    self._registry.register_factory(entity_type, factory)
