from __future__ import annotations

import importlib
import inspect
from typing import List, Type

import firefly.domain as ffd


class LoadApplicationServices(ffd.ApplicationService):
    _context_map: ffd.ContextMap = None
    _event_resolver: ffd.EventResolvingMiddleware = None
    _command_resolver: ffd.CommandResolvingMiddleware = None
    _query_resolver: ffd.QueryResolvingMiddleware = None

    def __call__(self, **kwargs):
        for context in self._context_map.contexts:
            for cls in self._load_module(context):
                self._register_service(cls, context)

        self.dispatch(ffd.ApplicationServicesLoaded())

    def _register_service(self, cls: Type[ffd.ApplicationService], context: ffd.Context):
        if not cls.has_handlers():
            return

        if cls.has_listeners():
            for config in cls.get_listeners():
                self._event_resolver.add_event_listener(cls, config['event'])
                if cls not in context.event_listeners:
                    context.event_listeners[cls] = []
                context.event_listeners[cls].append(config['event'])

        if cls.has_command_handlers():
            for config in cls.get_command_handlers():
                self._command_resolver.add_command_handler(cls, config['command'])
                context.command_handlers[cls] = config['command']

        if cls.has_query_handlers():
            for config in cls.get_query_handlers():
                self._query_resolver.add_query_handler(cls, config['query'])
                context.query_handlers[cls] = config['query']

    @staticmethod
    def _load_module(context: ffd.Context) -> List[Type[ffd.ApplicationService]]:
        module_name = context.config.get('application_service_module', '{}.application.service')
        try:
            module = importlib.import_module(module_name.format(context.name))
        except (ModuleNotFoundError, KeyError):
            return []

        ret = []
        for k, v in module.__dict__.items():
            if not inspect.isclass(v):
                continue
            if issubclass(v, ffd.ApplicationService):
                ret.append(v)

        return ret
