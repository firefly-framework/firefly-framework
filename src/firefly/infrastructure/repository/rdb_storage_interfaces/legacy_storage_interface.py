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

from abc import abstractmethod, ABC
from typing import Type

import firefly.domain as ffd

from ..rdb_storage_interface import RdbStorageInterface


class LegacyStorageInterface(RdbStorageInterface, ffd.LoggerAware, ABC):
    _template_prefix = 'sql'

    def _add(self, entity: ffd.Entity):
        return self._execute(*self._generate_query(entity, f'{self._template_prefix}/insert.sql', {
            'data': {
                entity.id_name(): entity.id_value(),
                'document': self._serializer.serialize(entity),
            }
        }))

    def _all(self, entity_type: Type[ffd.Entity], criteria: ffd.BinaryOp = None, limit: int = None, offset: int = None):
        return self._execute(*self._generate_query(entity_type, f'{self._template_prefix}/select.sql', {
            'columns': ('document',),
            'criteria': criteria,
        }))

    def _find(self, uuid: str, entity_type: Type[ffd.Entity]):
        return self._execute(*self._generate_query(entity_type, f'{self._template_prefix}/select.sql', {
            'columns': ('document',),
            'criteria': ffd.Attr(entity_type.id_name()) == uuid,
        }))

    def _remove(self, entity: ffd.Entity):
        return self._execute(*self._generate_query(entity, f'{self._template_prefix}/delete.sql', {
            'columns': ('document',),
            'criteria': ffd.Attr(entity.id_name()) == entity.id_value(),
        }))

    def _update(self, entity: ffd.Entity):
        return self._execute(*self._generate_query(entity, f'{self._template_prefix}/update.sql', {
            'data': {
                entity.id_name(): entity.id_value(),
                'document': self._serializer.serialize(entity),
            }
        }))

    def _migrate_table(self, entity: Type[ffd.Entity]):
        pass

    @abstractmethod
    def _build_entity(self, entity: Type[ffd.Entity], data, raw: bool = False):
        pass

    @abstractmethod
    def _execute(self, sql: str, params: dict = None):
        pass

    @abstractmethod
    def _ensure_connected(self):
        pass

    @abstractmethod
    def _disconnect(self):
        pass
