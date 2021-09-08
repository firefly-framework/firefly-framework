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


class Authenticator(ConfigurationAnnotation):
    def __call__(self, *args, **kwargs):
        def authenticator_wrapper(cls: ffd.MetaAware):
            try:
                cls.add_annotation(self)
            except AttributeError:
                raise ffd.FrameworkError('@authenticator used on invalid target')
            return cls

        return authenticator_wrapper

    def configure(self, cls: Any, container):
        if not issubclass(cls, ffd.Handler):
            raise ffd.ConfigurationError('Authenticators must be a subclass of Handler')
        container.authenticator.add(container.build(cls))


authenticator = Authenticator()
