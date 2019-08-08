from __future__ import annotations

from typing import Union

from .framework_annotation import FrameworkAnnotation


class On(FrameworkAnnotation):
    CRUD_ACTIONS = ['create', 'retrieve', 'update', 'delete']

    def name(self) -> str:
        return '__ff_listener'

    def __call__(self, event: Union[str, type], action: str = None):
        kwargs = {'event': event}
        if action in self.CRUD_ACTIONS:
            kwargs['crud'] = action
        return super()._attach_annotation(**kwargs)


on = On()
