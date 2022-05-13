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

import os
import uuid

from devtools import debug
from dotenv import load_dotenv
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import inspect, MetaData
from sqlalchemy.orm import declarative_base

import firefly.domain as ffd
from firefly.domain.service.entity.pydantic_model_from_entity import pydantic_model_from_entity

load_dotenv()

meta = MetaData(schema=os.environ.get('CONTEXT'))
Base = declarative_base(metadata=meta)


class Entity(Base):
    __abstract__ = True
    _logger = None

    @staticmethod
    def __try_update_forward_refs__():
        pass

    def __init__(self, *args, **kwargs):
        if kwargs.get(self.id_name(), None) is None:
            kwargs[self.id_name()] = uuid.uuid4()
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.id_value() == other.id_value()

    def to_dict(self):
        return self.pydantic_model().from_orm(self).dict()

    @classmethod
    def from_dict(cls, data: dict):
        print(cls.pydantic_model().schema())
        return cls({
            k: v
            for k, v in data.items() if k in cls._sa_class_manager
        })
        # return cls(**ffd.build_argument_list(data, cls))

    def id_value(self):
        return getattr(self, self.id_name(self.__class__))

    @classmethod
    def id_name(cls):
        ret = list(map(lambda x: x.name, inspect(cls).primary_key))
        return ret if len(ret) > 1 else ret[0]

    @classmethod
    def pydantic_model(cls):
        if not hasattr(cls, '__ff_cache__'):
            cls.__ff_cache__ = {
                cls.__name__: pydantic_model_from_entity(cls)
            }
        elif cls.__name__ not in getattr(cls, '__ff_cache__'):
            cls.__ff_cache__[cls.__name__] = pydantic_model_from_entity(cls)

        return cls.__ff_cache__[cls.__name__]
