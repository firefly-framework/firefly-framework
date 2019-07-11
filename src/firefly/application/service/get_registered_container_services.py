from __future__ import annotations

import firefly.domain as ffd


class GetRegisteredContainerServices(ffd.Service):
    _context_map: ffd.ContextMap = None

    def __call__(self, flatten: bool = False, context: str = None, **kwargs) -> dict:
        ret = {}
        contexts = {context: self._context_map.get_context(
            context)} if context is not None else self._context_map.contexts
        if context is None:
            contexts.update(self._context_map.extensions)

        for context in contexts.values():
            ret[context.name] = [(k, f'{v.__module__}.{v.__name__}')
                                 for k, v in
                                 context.container.get_registered_services().items()]
            if flatten:
                for subcontainer in context.container.child_containers:
                    if subcontainer is not None:
                        ret[context.name].extend(
                            [(k, v) for k, v in subcontainer.get_registered_services().items()])

        return ret
