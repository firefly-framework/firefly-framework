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

from typing import Callable

from firefly.presentation.web.polyfills import *  # __:skip
from firefly.presentation.web.js_libs.mithril import m

from firefly import SystemBus, Middleware, EventBus, domain as ffd, CommandBus, QueryBus, MessageFactory


# __pragma__('kwargs')
class LoggingMiddleware(Middleware):
    def __init__(self, prefix: str = ''):
        self.prefix = prefix

    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        console.log(self.prefix, message)
        return next_(message)


class CommandHandlingMiddleware(Middleware):
    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return m.request({
            'method': 'POST',
            'url': f'{process.env.FF_HOST}/{message.get_context()}',
            'body': message.to_dict(),
        })


class QueryHandlingMiddleware(Middleware):
    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        return m.request({
            'method': 'GET',
            'url': f'{process.env.FF_HOST}/{message.get_context()}',
            'params': {
                'query': JSON.stringify(message.to_dict()),
            },
        })
# __pragma__('nokwargs')


message_factory = MessageFactory()
bus = SystemBus()
bus._event_bus = EventBus([
    LoggingMiddleware('Event Bus'),
])
# noinspection PyProtectedMember
bus._event_bus._message_factory = message_factory

bus._command_bus = CommandBus([
    LoggingMiddleware('Command Bus'),
    CommandHandlingMiddleware(),
])
# noinspection PyProtectedMember
bus._command_bus._message_factory = message_factory

bus._query_bus = QueryBus([
    LoggingMiddleware('Query Bus'),
    QueryHandlingMiddleware(),
])
# noinspection PyProtectedMember
bus._query_bus._message_factory = message_factory
