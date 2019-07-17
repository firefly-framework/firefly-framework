from __future__ import annotations

from collections import Callable
from dataclasses import fields, make_dataclass
from typing import List, get_type_hints

import firefly.domain as ffd
import inflection

from .framework_annotation import FrameworkAnnotation


class Crud(FrameworkAnnotation):
    OPS = ('create', 'delete', 'update', 'get')

    def name(self) -> str:
        return '__ff_port'

    def cli(self, target: ffd.Entity, params: dict = None, exclude: List[str] = None):
        def wrapper(cls, exclude_=exclude or [], params_=params or {}):
            for op in self.OPS:
                if op in exclude_:
                    continue
                ffd.cli(
                    name=inflection.dasherize('{}-{}'.format(op, target.__name__)).lower(),
                    params=target.get_params(op),
                    target='crud::{}.{}::{}'.format(target.__module__, target.__name__, op),
                    **params_
                )(cls)
            return cls
        return wrapper

    def http(self, target: ffd.Entity, params: dict = None, exclude: List[str] = None):
        def wrapper(cls, exclude_=exclude or [], params_=params or {}):
            for op in self.OPS:
                if op in exclude_:
                    continue
                for method, path, _ in self._rest_endpoints(target, op):
                    ffd.http(
                        path=path,
                        method=method,
                        target=self._build_command_query(target, op),
                        **params_
                    )(cls)
            for method, path, op in self._collection_endpoints(target):
                ffd.http(
                    path=path,
                    method=method,
                    target=self._build_command_query(target, op),
                    **params_
                )(cls)
            return cls
        return wrapper

    def _rest_endpoints(self, entity: ffd.Entity, op: str, prefix: str = ''):
        slug = self._entity_slug(entity)
        id_ = self._id_slug(entity)
        if op == 'create':
            return [('POST', '{}/{}'.format(prefix, slug), op)]
        if op == 'update':
            return [('POST', '{}/{}/{{{}}}'.format(prefix, slug, id_), op)]
        if op == 'delete':
            return [('DELETE', '{}/{}/{{{}}}'.format(prefix, slug, id_), op)]
        if op == 'get':
            return [('GET', '{}/{}'.format(prefix, slug), op), ('GET', '{}/{}/{{{}}}'.format(prefix, slug, id_), op)]

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

    @staticmethod
    def _build_command_query(entity: ffd.Entity, op: str):
        base = ffd.CrudCommand
        if op == 'get':
            base = ffd.CrudQuery

        fields_ = []
        for name, config in entity.get_params(op).items():
            if config['default'] == []:
                continue
            fields_.append((name, config['type'], config['default']))

        cls = make_dataclass('{}{}'.format(inflection.camelize(op), entity.__name__), fields_, bases=(base,))

        def wrapper(*args, **kwargs):
            ret = cls()
            ret.headers['entity_fqn'] = '{}.{}'.format(entity.__module__, entity.__name__)
            ret.headers['operation'] = op
            return ret

        return wrapper


crud = Crud()
