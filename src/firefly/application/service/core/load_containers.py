from __future__ import annotations

import importlib

import firefly.domain as ffd
import firefly_di as di


class LoadContainers(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _container: di.Container = None

    def __call__(self):
        for extension in self._context_map.extensions:
            extension.container = self._load_module(extension.name, extension.config)
            self.dispatch(ffd.ContainerInitialized(context=extension.name))

        for context in self._context_map.contexts:
            context.container = self._load_module(context.name, context.config)
            for name, config in context.config.get('extensions', {}).items():
                context.container.register_container(self._context_map.get_extension(name).container)
            self.dispatch(ffd.ContainerInitialized(context=context.name))

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
        container.register_container(self._container)

        return container
