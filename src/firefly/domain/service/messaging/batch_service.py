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

from datetime import datetime
from typing import Type

from ..cache.cache import Cache
from ..core.application_service import ApplicationService
from ..core.domain_service import DomainService
from ..serialization.serializer import Serializer
from ...entity.core.context_map import ContextMap


class BatchService(DomainService):
    _cache: Cache = None
    _serializer: Serializer = None
    _context_map: ContextMap = None
    _batch_registry: dict = {}

    def handle(self, service: Type[ApplicationService], params: dict):
        if '_batch' in params:
            print("_batch is in the message. Processing.")
            return self._context_map.locate_service(service.__name__)(params['_batch'])

        print("Adding message to batch")
        messages = self._cache.add(self._key(service), self._serializer.serialize(params))
        print(f"Messages: {messages}")
        print(len(messages))
        if len(messages) == self._batch_registry[service]['batch_size']:
            print("We've met the batch size. Flushing.")
            return self.flush(service)

        return None

    def flush(self, service: Type[ApplicationService]):
        print("flush: deleting messages")
        messages = self._cache.delete(self._key(service))
        print(f"Got: {messages}")
        if messages is not None and len(messages) > 0:
            print("processing messages")
            messages = list(map(self._serializer.deserialize, messages))
            if self._batch_registry[service]['message_type'] == 'command':
                return self.invoke(self._batch_registry[service]['message'], data={
                    '_batch': messages,
                }, async_=True)
            else:
                return self.dispatch(self._batch_registry[service]['message'], data={'_batch': messages})

        return None

    def register(self, service: Type[ApplicationService], batch_size: int, batch_window: int, message: str,
                 message_type: str):
        self._batch_registry[service] = {
            'batch_size': batch_size,
            'batch_window': batch_window,
            'message_type': message_type,
            'message': message,
        }

    def is_registered(self, service: Type[ApplicationService]):
        return service in self._batch_registry

    def flush_all(self):
        last_run = datetime.fromtimestamp(self._cache.get('flush-all-last-run'))
        delta = (datetime.utcnow() - last_run).seconds
        for service, config in self._batch_registry.items():
            if delta >= config.get('batch_window'):
                self.flush(service)
        self._cache.set('flush-all-last-run', datetime.utcnow().timestamp())

    def _key(self, service: Type[ApplicationService]):
        return f'{service.__name__}Batch'
