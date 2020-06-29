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

from typing import List, Union

import firefly as ff
import firefly.domain as ffd
import firefly_di as di
from firefly.domain.entity.core.cli_app import CliApp
from firefly.domain.entity.core.cli_endpoint import CliEndpoint

from ..aggregate_root import AggregateRoot
from ..entity import list_, hidden


class ContextMap(AggregateRoot):
    contexts: List[ffd.Context] = list_()
    _config: ffd.Configuration = hidden()
    _firefly_container: di.Container = hidden()

    def __post_init__(self):
        for name, config in self._config.contexts.items():
            if config is not False:
                self.contexts.append(ffd.Context(
                    name=name,
                    config=config or {},
                    is_extension=config.get('is_extension', False) if isinstance(config, dict) else False
                ))

        found = False
        for context in self.contexts:
            if context.name == 'firefly':
                found = True
                context.container = self._firefly_container
                break
        if not found:
            c = ffd.Context(name='firefly', config={})
            c.container = self._firefly_container
            self.contexts.append(c)

    def get_context(self, name: str):
        for context in self.contexts:
            if context.name == name:
                return context

    def find_entity_by_name(self, context_name: str, entity_name: str):
        for entity in self.get_context(context_name).entities:
            if entity.__name__ == entity_name:
                return entity

    def locate_service(self, name: str):
        ret = self.locate_command_handler(name)
        if ret is None:
            ret = self.locate_event_listener(name)
        if ret is None:
            ret = self.locate_query_handler(name)

        return ret

    def locate_command_handler(self, command: ff.TypeOfCommand):
        context_name = self._get_context_name_from_message(command)
        context = self.get_context(context_name)

        for command_handler, cmd in context.command_handlers.items():
            if cmd == command:
                return command_handler

    def locate_event_listener(self, event: ff.TypeOfEvent):
        context_name = self._get_context_name_from_message(event)
        context = self.get_context(context_name)

        for event_listener, events in context.command_handlers.items():
            if event in events:
                return event_listener

    def locate_query_handler(self, query: ff.TypeOfQuery):
        context_name = self._get_context_name_from_message(query)
        context = self.get_context(context_name)

        for query_handler, qry in context.command_handlers.items():
            if qry == query:
                return query_handler

    @staticmethod
    def _get_context_name_from_message(message: Union[str, ffd.Message]):
        if isinstance(message, str):
            return message.split('.')[0]
        return message.get_context()

    def get_cli_app(self, name: str):
        app = CliApp(name=name)
        for context in self.contexts:
            for endpoint in context.endpoints:
                if isinstance(endpoint, CliEndpoint) and endpoint.app == name:
                    app.endpoints.append(endpoint)
        return app
