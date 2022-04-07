from __future__ import annotations

import os
from functools import lru_cache
from typing import Callable, Optional

import firefly.domain as ffd


if os.environ.get('ADAPTIVE_MEMORY'):
    @ff.register_middleware(index=0, buses=['event', 'command'])
    class AdaptiveMemoryRoutingMiddleware(ffd.Middleware, ffd.ResourceNameGenerator, ffd.LoggerAware):
        _resource_monitor: ResourceMonitor = None
        _execution_context: ExecutionContext = None
        _message_transport: ff.MessageTransport = None
        _configuration: ff.Configuration = None
        _context: str = None

        def __init__(self):
            context = self._configuration.contexts['firefly_aws']
            if context.get('memory_async') == 'adaptive':
                self._memory_settings = sorted(list(map(int, context.get('memory_settings'))))
                if self._memory_settings is None:
                    raise ff.ConfigurationError(
                        'When using "adaptive" memory you must provide a list of memory_settings'
                    )
                self._memory_mappings = self._configuration.contexts[self._context].get('memory_settings', {})

        def __call__(self, message: ff.Message, next_: Callable) -> Optional[ff.Message]:
            function_name = self._lambda_function_name(self._context, 'Async')
            if self._execution_context.context and self._execution_context.context.function_name == function_name:
                if str(message) in self._memory_mappings:
                    setattr(message, '_memory', self._memory_mappings[str(message)])
                elif 'default' in self._memory_mappings:
                    setattr(message, '_memory', self._memory_mappings['default'])

                if not hasattr(message, '_memory'):
                    memory = self._get_memory_level(str(message))
                    if memory is None:
                        self._resource_monitor.set_memory_level(str(message), self._memory_settings[0])
                        setattr(message, '_memory', str(self._memory_settings[0]))
                        self._get_memory_level.cache_clear()
                    else:
                        setattr(message, '_memory', self._get_memory_level(str(message)))

                self.info('Routing message %s to %s', str(message), self._lambda_function_name(
                    self._context, type_='Async', memory=getattr(message, '_memory')
                ))
                self._enqueue_message(message)

                return

            else:
                return next_(message)

        def _enqueue_message(self, message: ff.Message):
            if isinstance(message, ff.Event):
                self._message_transport.dispatch(message)
            elif isinstance(message, ff.Command):
                setattr(message, '_async', True)
                self._message_transport.invoke(message)

        @lru_cache(maxsize=None)
        def _get_memory_level(self, message: str):
            return self._resource_monitor.get_memory_level(message)
