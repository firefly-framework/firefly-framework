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
from abc import ABC, abstractmethod
from typing import Callable


class FrameworkAnnotation(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    def _attach_annotation(self, child_callback: Callable = None, **kwargs):
        def wrapper(cls):
            # if 'command' in kwargs and kwargs['command'] is None:
            #     kwargs['command'] = f'{cls.__module__.split(".")[0]}.{cls.__name__}'
            #     print(kwargs)
            prop = []
            if hasattr(cls, self.name()):
                prop = getattr(cls, self.name())
            args = self._callback(cls, kwargs)
            if isinstance(args, list):
                prop.extend(args)
            else:
                prop.append(args)
            setattr(cls, self.name(), prop)

            if child_callback is not None and inspect.isclass(cls):
                for k, v in cls.__dict__.items():
                    if hasattr(v, self.name()):
                        child_callback(cls, v)

            return cls

        return wrapper

    @staticmethod
    def _callback(cls, kwargs):
        return kwargs
