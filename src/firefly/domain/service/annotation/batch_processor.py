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

from .configuration_annotation import ConfigurationAnnotation


class BatchProcessor(ConfigurationAnnotation):
    def __call__(self, batch_size: int, batch_window: int = 300):
        def batch_wrapper(cls: ffd.MetaAware):
            try:
                cls.add_annotation(self)
                setattr(cls, '_batch_size', batch_size)
                setattr(cls, '_batch_window', batch_window)
            except AttributeError:
                raise ffd.FrameworkError('@authenticator used on invalid target')
            return cls

        return batch_wrapper

    def configure(self, cls: Any, container):
        if not issubclass(cls, ffd.ApplicationService):
            raise ffd.ConfigurationError('@batch_processor must be used on an ApplicationService')

        container.batch_service.register(
            cls,
            batch_size=getattr(cls, '_batch_size'),
            batch_window=getattr(cls, '_batch_window'),
            message_type='event' if cls.is_event_listener() else 'command',
            message=cls.get_command() if cls.is_command_handler() else cls.get_events()[0]
        )


batch_processor = BatchProcessor()
