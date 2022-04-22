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

from typing import Type

import firefly as ff
import inflection
from firefly.domain.entity.entity import Entity
from firefly.domain.service.core.application_service import ApplicationService
from firefly.domain.service.logging.logger import LoggerAware


class AutoGenerateAggregateApis(ApplicationService, LoggerAware):
    _kernel: ff.Kernel = None
    _context: str = None

    def __call__(self):
        for entity in self._kernel.get_entities():
            if entity.get_class_context() != self._context:
                entity._context = self._context
            self._process_entity(entity)

    def _process_entity(self, entity: type):
        if not issubclass(entity, ff.AggregateRoot) or entity == ff.AggregateRoot:
            return

        self._create_crud_command_handlers(entity)
        self._create_query_handler(entity)

    def _create_query_handler(self, entity: Type[Entity]):
        query_name = inflection.pluralize(entity.__name__)

        class Query(ff.QueryService[entity]):
            pass

        Query.__name__ = query_name

        self._kernel.register_query(ff.query_handler()(Query))

    def _create_crud_command_handlers(self, entity: Type[Entity]):
        for action in ('Create', 'Delete', 'Update'):
            self._create_crud_command_handler(entity, action)

    def _create_crud_command_handler(self, entity, name_prefix):
        name = f'{name_prefix}Entity'
        base = getattr(ff, name)

        class Action(base[entity]):
            pass

        Action.__name__ = f'{name_prefix}{entity.__name__}'

        self._kernel.register_command(ff.command_handler()(Action))
