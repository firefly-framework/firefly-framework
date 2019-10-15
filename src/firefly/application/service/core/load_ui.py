from __future__ import annotations

import importlib
import inspect
from typing import List

import firefly.domain as ffd


class LoadUi(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            for obj in self._load_module(context):
                context.ports.append(obj)

        self.dispatch(ffd.UiLoaded())

    @staticmethod
    def _load_module(context: ffd.Context) -> List[object]:
        module_name = context.config.get('ui_module', '{}.ui')
        try:
            module = importlib.import_module(module_name.format(context.name))
        except (ModuleNotFoundError, KeyError):
            return []

        ret = []
        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if hasattr(v, '__ff_port'):
                ret.append(v)

        return ret
