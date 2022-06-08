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

import inspect
import typing
from dataclasses import fields
from datetime import datetime, date
from typing import List, Union, Dict
from typing import get_origin, get_args

import inflection
import marshmallow_dataclass
from marshmallow import Schema, ValidationError, EXCLUDE
from pydantic import BaseModel
from sqlalchemy.exc import InvalidRequestError

import firefly.domain as ffd
from firefly.domain.entity.validation.validators import IsValidEmail, HasLength, MatchesPattern, IsValidUrl, \
    IsLessThanOrEqualTo, IsLessThan, IsGreaterThanOrEqualTo, IsGreaterThan, IsMultipleOf, HasMaxLength, HasMinLength, \
    parse
from firefly.domain.meta.build_argument_list import build_argument_list
from firefly.domain.utils import is_type_hint
from .event_buffer import EventBuffer
from .generic_base import GenericBase
from .parameter import Parameter


class Empty:
    pass


_defs = {}


class ValueObject:
    _cache = {}

    def __init__(self, **kwargs):
        pass

    def to_dict(self, skip: list = None, force_all: bool = False, **kwargs):
        caller = kwargs.get('caller')
        include_relationships = kwargs.get('include_relationships', True)
        ret = self.schema().dump(self)

        if include_relationships:
            types = typing.get_type_hints(self.__class__)
            for field_ in fields(self):
                if field_.name.startswith('_'):
                    continue
                t = types[field_.name]
                if t is caller.__class__ and caller == getattr(self, field_.name):
                    continue
                if inspect.isclass(t) and issubclass(t, ValueObject):
                    try:
                        ret[field_.name] = getattr(self, field_.name).to_dict(
                            skip=skip, force_all=force_all, caller=self
                        )
                    except AttributeError:
                        pass
                elif is_type_hint(t) and get_origin(t) is list:
                    args = get_args(t)
                    if args[0] is caller.__class__:
                        continue
                    if inspect.isclass(args[0]) and issubclass(args[0], ValueObject):
                        try:
                            ret[field_.name] = [
                                e.to_dict(skip=skip, force_all=force_all, caller=self)
                                for e in getattr(self, field_.name)
                            ]
                        except AttributeError:
                            pass

        if skip is not None:
            for s in skip:
                if s in ret:
                    del ret[s]

        if force_all is False:
            for field in fields(self.__class__):
                if field.metadata.get('internal') is True:
                    del ret[field.name]

        return ret

    def load_dict(self, d: dict):
        data = build_argument_list(d.copy(), self.__class__, strict=False, include_none_parameters=True)
        t = typing.get_type_hints(self.__class__)
        for name, type_ in t.items():
            if name in data:
                if inspect.isclass(type_) and issubclass(type_, (datetime, date)) and isinstance(data[name], str):
                    setattr(self, name, parse(data[name], ignoretz=True))
                elif inspect.isclass(type_) and issubclass(type_, ValueObject) and isinstance(data[name], type_):
                    existing = getattr(self, name)
                    if existing is None:
                        setattr(self, name, data[name])
                    elif name in d and isinstance(d[name], dict):
                        existing.load_dict(d[name])
                else:
                    try:
                        if data[name] is not None and not isinstance(data[name], type_):
                            setattr(self, name, type_(data[name]))
                        else:
                            setattr(self, name, data[name])
                    except TypeError:
                        setattr(self, name, data[name])

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
                return cls.schema().load(build_argument_list(data, cls), unknown=EXCLUDE, partial=True)
            except:
                return cls.schema().load(data, unknown=EXCLUDE, partial=True)
        except ValidationError as e:
            missing = list(filter(lambda f: not f.startswith('_'), e.args[0].keys()))
            if len(missing) > 0:
                raise ffd.MissingArgument(
                    f"Missing {len(missing)} required argument(s) for class {cls.__name__}: {', '.join(missing)}"
                ) from e
            raise e

    def debug(self, *args, **kwargs):
        return self._logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self._logger.error(*args, **kwargs)

    @classmethod
    def schema(cls) -> Schema:
        if not isinstance(cls._cache, dict):
            cls._cache = {}

        if cls not in cls._cache:
            cls._cache[cls] = marshmallow_dataclass.class_schema(cls)()

        return cls._cache[cls]

    def __str__(self):
        while True:
            try:
                return self.__repr__()
            except InvalidRequestError:
                ret = self.__class__.__name__ + '('
                props = []
                for f in fields(self):
                    props.append(f"{f.name}={getattr(self, f.name)}")
                return f"{self.__class__.__name__}({', '.join(props)})"
            except AttributeError as e:
                if 'object has no attribute' in str(e):
                    attr = str(e).split(' ')[-1].strip("'")
                    setattr(self, attr, None)
                else:
                    raise e
