from __future__ import annotations

import firefly.domain as ffd
import firefly_di as di

from .application_service import ApplicationService


class AddApplicationService(ApplicationService):
    _container: di.Container = None
    _event_resolver: ffd.EventResolvingMiddleware = None
    _command_resolver = ffd.CommandResolvingMiddleware = None
    _query_resolver = ffd.QueryResolvingMiddleware = None

    def __call__(self, fqn: str, args: dict = None):
        args = args or {}
        cls = ffd.load_class(fqn)
        for key in ('__ff_command_handler', '__ff_listener', '__ff_query_handler'):
            if hasattr(cls, key):
                mw = ffd.ServiceExecutingMiddleware(self._container.build(cls, **args))
                setattr(mw, key, getattr(cls, key))
                self._add_middleware(mw)
