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
from datetime import datetime
from typing import Type, Union

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

    def handle(self, service: ApplicationService, params: dict):
        if '_batch' in params:
            return service(params['_batch'])

        messages = self._cache.add(self._key(service), self._serializer.serialize(params))
        if len(messages) == self._batch_registry[service.__class__]['batch_size']:
            return self.flush(service)

        return None

    def flush(self, service: ApplicationService):
        messages = self._cache.delete(self._key(service))
        if messages is not None and len(messages) > 0:
            self.info(f'Processing batch for service: {service}')
            messages = list(map(self._serializer.deserialize, messages))
            if self._batch_registry[service.__class__]['message_type'] == 'command':
                self.info('Invoking command')
                return self.invoke(self._batch_registry[service.__class__]['message'], data={
                    '_batch': messages,
                }, async_=True)
            else:
                self.info('Dispatching event')
                return self.dispatch(self._batch_registry[service.__class__]['message'], data={'_batch': messages})

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
        last_runs = self._cache.get('flush-all-last-runs') or {}
        for service, config in self._batch_registry.items():
            key = service.__name__
            if key not in last_runs:
                last_runs[key] = datetime(year=1970, month=1, day=1).timestamp()
            delta = (datetime.utcnow() - datetime.fromtimestamp(last_runs[key])).seconds
            if delta >= config.get('batch_window'):
                self.info(f'Flushing {service}')
                self.flush(service)
                last_runs[key] = datetime.utcnow().timestamp()
        self._cache.set('flush-all-last-runs', last_runs)

    def _key(self, service: Union[Type[ApplicationService], ApplicationService]):
        return f'{service.__class__.__name__}Batch' if not inspect.isclass(service) else service.__name__
