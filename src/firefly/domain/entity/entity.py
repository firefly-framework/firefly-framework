#  Copyright (c) 2019 JD Williams
#
#  This file is part of Firefly, a Python SOA framework built by JD Williams. Firefly is free software; you can
#  redistribute it and/or modify it under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or (at your option) any later version.
#
#  Firefly is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
#  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details. You should have received a copy of the GNU Lesser General Public
#  License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  You should have received a copy of the GNU General Public License along with Firefly. If not, see
#  <http://www.gnu.org/licenses/>.

from __future__ import annotations

import inspect
import os
import uuid
from datetime import datetime, date
from typing import get_origin, get_args, get_type_hints

import inflection
from dotenv import load_dotenv
from marshmallow import Schema, fields as m_fields, ValidationError, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import inspect as sa_inspect, MetaData
from sqlalchemy.orm import declarative_base

import firefly.domain as ffd
from firefly.domain.utils import is_type_hint

load_dotenv(dotenv_path=os.path.abspath(os.curdir) + '/.env')

meta = MetaData(schema=os.environ.get('CONTEXT'))
Base = declarative_base(metadata=meta)


MARSHMALLOW_MAPPINGS = {
    str: m_fields.Str,
    int: m_fields.Int,
    float: m_fields.Float,
    bool: m_fields.Bool,
    datetime: m_fields.DateTime,
    date: m_fields.Date,
}


class Entity(Base):
    __abstract__ = True
    _logger = None
    _cache = {}
    _session = None

    def __init__(self, *args, **kwargs):
        if kwargs.get(self.id_name(), None) is None:
            kwargs[self.id_name()] = uuid.uuid4()
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.id_value() == other.id_value()

    def to_dict(self, skip: list = None, **kwargs):
        caller = kwargs.get('caller')
        include_relationships = kwargs.get('include_relationships', True)
        ret = self.schema().dump(self)

        if include_relationships:
            types = get_type_hints(self.__class__)
            for field_name in self.__mapper__.class_manager.keys():
                if field_name.startswith('_'):
                    continue
                t = types[field_name]
                if t is caller.__class__ and caller == getattr(self, field_name):
                    continue
                if inspect.isclass(t) and issubclass(t, (ffd.ValueObject, ffd.Entity)):
                    try:
                        ret[field_name] = getattr(self, field_name).to_dict(
                            skip=skip, caller=self
                        )
                    except AttributeError:
                        pass
                elif is_type_hint(t) and get_origin(t) is list:
                    args = get_args(t)
                    if args[0] is caller.__class__:
                        continue
                    if inspect.isclass(args[0]) and issubclass(args[0], (ffd.ValueObject, ffd.Entity)):
                        try:
                            ret[field_name] = [
                                e.to_dict(skip=skip, caller=self)
                                for e in getattr(self, field_name)
                            ]
                        except AttributeError:
                            pass

        if skip is not None:
            for s in skip:
                if s in ret:
                    del ret[s]

        return ret

    @classmethod
    def from_dict(cls, data: dict, map_: dict = None, skip: list = None):
        if map_ is not None:
            d = data.copy()
            for source, target in map_.items():
                if source in d:
                    d[target] = d[source]
            data = d

        if skip is not None:
            d = data.copy()
            for k in data.keys():
                if k in skip:
                    del d[k]
            data = d

        for k, v in list(data.items()).copy():
            if k.endswith('_'):
                data[str(k).rstrip('_')] = v
                del data[k]
        try:
            for k in list(data.keys()).copy():
                if k.startswith('_'):
                    del data[k]
            try:
                return cls.schema().load(data, session=cls._session, unknown=EXCLUDE, partial=True)
            except TypeError:
                return cls.schema().load(data, unknown=EXCLUDE, partial=True)
        except ValidationError as e:
            missing = list(filter(lambda f: not f.startswith('_'), e.args[0].keys()))
            if len(missing) > 0:
                raise ffd.MissingArgument(
                    f"Missing {len(missing)} required argument(s) for class {cls.__name__}: {', '.join(missing)}"
                ) from e
            raise e

    def load_dict(self, data: dict):
        for field_name in self.__mapper__.class_manager.keys():
            if field_name in data:
                setattr(self, field_name, data[field_name])

    @classmethod
    def match_id_from_argument_list(cls, args: dict):
        snake = f'{inflection.underscore(cls.__name__)}_id'
        if snake in args:
            return {snake: args[snake]}

        id_name = cls.id_name()
        if id_name in args:
            return {id_name: args[id_name]}

    def id_value(self):
        return getattr(self, self.id_name())

    @classmethod
    def id_name(cls):
        ret = list(map(lambda x: x.name, sa_inspect(cls).primary_key))
        return ret if len(ret) > 1 else ret[0]

    @classmethod
    def schema(cls) -> Schema:
        if not isinstance(cls._cache, dict):
            cls._cache = {}

        if cls not in cls._cache:
            class FieldContainer(SQLAlchemyAutoSchema):
                class Meta:
                    model = cls
                    include_relationships = True
                    load_instance = True

            cls._cache[cls] = FieldContainer()

        return cls._cache[cls]

    @classmethod
    def get_class_context(cls):
        return os.environ.get('CONTEXT')
