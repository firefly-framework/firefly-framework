from __future__ import annotations

import inspect
from abc import ABC
from typing import Union

import firefly.domain as ffd

from .entity import Entity


class AggregateRoot(Entity, ABC):
    pass


def aggregate_root(_cls=None, create_on: Union[ffd.Event, str] = None, delete_on: Union[ffd.Event, str] = None,
                   update_on: Union[ffd.Event, str] = None, **kwargs):
    ret = ffd.generate_dc(AggregateRoot, _cls, **kwargs)

    if create_on is not None:
        def wrapper(cls, wrap=ret):
            return wrap(ffd.on(create_on, action='create')(cls))
        ret = wrapper

    if delete_on is not None:
        def wrapper(cls, wrap=ret):
            return wrap(ffd.on(delete_on, action='delete')(cls))
        ret = wrapper

    if update_on is not None:
        def wrapper(cls, wrap=ret):
            return wrap(ffd.on(update_on, action='update')(cls))
        ret = wrapper

    return ret
