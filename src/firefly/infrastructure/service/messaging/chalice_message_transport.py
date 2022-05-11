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

from typing import Any

import firefly.domain as ffd
from chalice.test import Client


class ChaliceMessageTransport(ffd.MessageTransport, ffd.LoggerAware):
    _kernel: ffd.Kernel = None
    _serializer: ffd.Serializer = None
    _context: str = None

    __client: Client = None

    @property
    def _client(self):
        if self.__client is None:
            self.__client = self._kernel.get_application().get_test_client()
        return self.__client

    def dispatch(self, event: ffd.Event) -> None:
        if event.get_context() != self._context:
            self.info(f'dispatch(): Message {event} is for another context. Skipping.')
        else:
            self._client.lambda_.invoke(
                'sqs_event',
                self._client.events.generate_sqs_event([self._serializer.serialize(event)])
            )

    def invoke(self, command: ffd.Command) -> Any:
        return self._client.lambda_.invoke(
            str(command).split('.').pop(), self._serializer.serialize(command)
        ).payload

    def request(self, query: ffd.Query) -> Any:
        return self._client.lambda_.invoke(
            str(query).split('.').pop(), self._serializer.serialize(query)
        ).payload
