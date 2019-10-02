from __future__ import annotations

import importlib
import inspect

import firefly.domain as ffd


class LoadEntities(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None

    def __call__(self, **kwargs):
        for extension in self._context_map.extensions:
            self._load_module(extension)
            self.dispatch(ffd.DomainEntitiesLoaded(context=extension.name))
        for context in self._context_map.contexts:
            self._load_module(context)
            self.dispatch(ffd.DomainEntitiesLoaded(context=context.name))

    @staticmethod
    def _load_module(extension: ffd.Extension):
        module_name = extension.config.get('entity_module', '{}.domain.entity')
        try:
            module = importlib.import_module(module_name.format(extension.name))
        except (ModuleNotFoundError, KeyError):
            return

        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if issubclass(v, ffd.Entity):
                extension.entities.append(v)
