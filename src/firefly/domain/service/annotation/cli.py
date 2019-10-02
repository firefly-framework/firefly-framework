from __future__ import annotations

from typing import Union, Type, List

import firefly.domain as ffd

NAME: str = '__ff_cli'


def cli(target: Union[str, Type[ffd.ApplicationService]] = None, name: str = None, description: str = None,
        alias: dict = None, help_: dict = None, middleware: List[ffd.Middleware] = None, app_name: str = None):
    kwargs = locals()

    def wrapper(cls):
        if kwargs['name'] is None:
            kwargs['name'] = cls.__name__
        setattr(cls, NAME, kwargs)
        cls.__ff_port = True
        return cls

    return wrapper
