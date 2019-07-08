from __future__ import annotations

import inspect
from collections import Callable
from dataclasses import fields, MISSING
from typing import List, get_type_hints

import inflection

from .framework_annotation import FrameworkAnnotation


class Crud(FrameworkAnnotation):
    def name(self) -> str:
        return '__ff_port'

    def __call__(self, for_: type, type_: Callable, params: dict = None, exclude: List[str] = None):
        def wrapper(cls, exclude_=exclude, params_=params or {}):
            exclude_ = exclude_ or []
            for op in ('create', 'delete', 'update', 'get'):
                if op in exclude_:
                    continue
                type_(
                    name=inflection.dasherize('{}-{}'.format(op, for_.__name__)).lower(),
                    params=self._get_params(op, for_),
                    for_='crud::{}.{}::{}'.format(for_.__module__, for_.__name__, op),
                    **params_
                )(cls)
            return cls
        return wrapper

    # TODO Move this into the Entity class.
    def _get_params(self, op: str, entity: type):
        if op in ('create', 'update'):
            return self._get_create_update_params(entity)
        else:
            types = get_type_hints(entity)
            for field_ in fields(entity):
                if 'pk' in field_.metadata:
                    return {field_.name: {
                        'default': inspect.Parameter.empty,
                        'type': types[field_.name],
                    }}

    @staticmethod
    def _get_create_update_params(entity: type):
        ret = {}
        for field_ in fields(entity):
            types = get_type_hints(entity)
            default = inspect.Parameter.empty
            if field_.default != MISSING:
                default = field_.default
            elif field_.default_factory != MISSING:
                default = field_.default_factory()
            if 'required' in field_.metadata:
                default = inspect.Parameter.empty

            ret[field_.name] = {
                'default': default,
                'type': types[field_.name],
            }

        return ret


crud = Crud()
