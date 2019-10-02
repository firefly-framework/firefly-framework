from __future__ import annotations

from typing import List, Union

import firefly as ff
import firefly.domain as ffd
import firefly_di as di

from ..aggregate_root import AggregateRoot
from ..entity import list_, hidden


class ContextMap(AggregateRoot):
    contexts: List[ffd.Context] = list_()
    extensions: List[ffd.Extension] = list_()
    _config: ffd.Configuration = hidden()
    _firefly_container: di.Container = hidden()

    def __post_init__(self):
        for name, config in self._config.extensions.items():
            self.extensions.append(ffd.Extension(name=name, config=config))
        for name, config in self._config.contexts.items():
            self.contexts.append(ffd.Context(name=name, config=config))

        found = False
        for context in (self.extensions + self.contexts):
            if context.name == 'firefly':
                found = True
                break
        if not found:
            self.extensions.append(ffd.Extension(name='firefly', config={}))

    def get_context(self, name: str):
        for context in self.contexts:
            if context.name == name:
                return context

    def get_extension(self, name: str):
        for extension in self.extensions:
            if extension.name == name:
                return extension

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
        context = self.get_context(context_name) or self.get_extension(context_name)

        for command_handler, cmd in context.command_handlers.items():
            if cmd == command:
                return command_handler

    def locate_event_listener(self, event: ff.TypeOfEvent):
        context_name = self._get_context_name_from_message(event)
        context = self.get_context(context_name) or self.get_extension(context_name)

        for event_listener, events in context.command_handlers.items():
            if event in events:
                return event_listener

    def locate_query_handler(self, query: ff.TypeOfQuery):
        context_name = self._get_context_name_from_message(query)
        context = self.get_context(context_name) or self.get_extension(context_name)

        for query_handler, qry in context.command_handlers.items():
            if qry == query:
                return query_handler

    @staticmethod
    def _get_context_name_from_message(message: Union[str, ffd.Message]):
        if isinstance(message, str):
            return message.split('.')[0]
        return message.get_context()
