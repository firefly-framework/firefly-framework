from __future__ import annotations

from collections import Callable
from dataclasses import fields
from typing import List, get_type_hints

import firefly.domain as ffd
import inflection

from .framework_annotation import FrameworkAnnotation


class Crud(FrameworkAnnotation):
    OPS = ('create', 'delete', 'update', 'get')

    def name(self) -> str:
        return '__ff_port'

    def cli(self, for_: ffd.Entity, params: dict = None, exclude: List[str] = None):
        def wrapper(cls, exclude_=exclude or [], params_=params or {}):
            for op in self.OPS:
                if op in exclude_:
                    continue
                ffd.cli(
                    name=inflection.dasherize('{}-{}'.format(op, for_.__name__)).lower(),
                    params=for_.get_params(op),
                    for_='crud::{}.{}::{}'.format(for_.__module__, for_.__name__, op),
                    **params_
                )(cls)
            return cls
        return wrapper

    def http(self, for_: ffd.Entity, params: dict = None, exclude: List[str] = None):
        def wrapper(cls, exclude_=exclude or [], params_=params or {}):
            for op in self.OPS:
                if op in exclude_:
                    continue
                for method, path in self._rest_endpoints(for_, op):
                    ffd.http(
                        path=path,
                        method=method,
                        for_='crud::{}.{}::{}'.format(for_.__module__, for_.__name__, op),
                        **params_
                    )(cls)
            for method, path in self._collection_endpoints(for_):
                ffd.http(
                    path=path,
                    method=method,
                    for_='crud::{}.{}::{}'.format(for_.__module__, for_.__name__, op),
                    **params_
                )(cls)
            return cls
        return wrapper

    def _rest_endpoints(self, entity: ffd.Entity, op: str, prefix: str = ''):
        slug = self._entity_slug(entity)
        id_ = self._id_slug(entity)
        if op == 'create':
            return [('POST', '{}/{}'.format(prefix, slug))]
        if op == 'update':
            return [('POST', '{}/{}/{{{}}}'.format(prefix, slug, id_))]
        if op == 'delete':
            return [('DELETE', '{}/{}/{{{}}}'.format(prefix, slug, id_))]
        if op == 'get':
            return [('GET', '{}/{}'.format(prefix, slug)), ('GET', '{}/{}/{{{}}}'.format(prefix, slug, id_))]

    def _collection_endpoints(self, entity: ffd.Entity):
        ret = []
        types = get_type_hints(entity)
        prefix = '/{}/{{{}}}'.format(self._entity_slug(entity), self._id_slug(entity))
        for field_ in fields(entity):
            try:
                if types[field_.name]._name != 'List':
                    continue
            except AttributeError:
                continue
            collection_type = types[field_.name].__args__[0]
            for op in self.OPS:
                ret.extend(self._rest_endpoints(collection_type, op, prefix))

        return ret

    @staticmethod
    def _entity_slug(entity: ffd.Entity):
        return inflection.dasherize(inflection.tableize(entity.__name__))

    @staticmethod
    def _id_slug(entity: ffd.Entity):
        return '{}_id'.format(inflection.underscore(entity.__name__))


crud = Crud()
