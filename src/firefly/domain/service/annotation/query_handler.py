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

import os
from typing import Union

import firefly.domain.constants as const
import firefly.domain.error as error


class QueryHandler:
    def __call__(self, query: Union[str, type, None] = None):
        def query_wrapper(cls):
            try:
                setattr(cls, const.HTTP_ENDPOINTS, [query or f'{os.environ.get("CONTEXT")}.{cls.__name__}'])
            except AttributeError:
                raise error.FrameworkError('@query_handler used on invalid target')

            return cls

        return query_wrapper


query_handler = QueryHandler()
