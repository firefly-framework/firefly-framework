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

# __pragma__('skip')
from abc import ABC
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABC
?"""
# __pragma__ ('noecom')


class ContextAware(ABC):
    @classmethod
    def get_class_context(cls):
        if hasattr(cls, '_context') and cls._context is not None:
            return cls._context

        parts = cls.__module__.split('.')
        # KLUDGE For integration / acceptance testing
        return parts[0] if parts[0] != 'firefly_test' else parts[1]

    @classmethod
    def set_class_context(cls, context_name: str):
        cls._context = context_name

    @classmethod
    def get_fqn(cls):
        if hasattr(cls, '_context') and cls._context is not None:
            context = cls._context
        else:
            context = cls.get_class_context()
        return f'{context}.{cls.__name__}'
