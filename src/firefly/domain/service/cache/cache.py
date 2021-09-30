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

from abc import ABC, abstractmethod
from typing import Any


class Cache(ABC):
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = None, **kwargs) -> Any:
        pass

    @abstractmethod
    def get(self, key: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def delete(self, key: str, **kwargs):
        pass

    @abstractmethod
    def clear(self, **kwargs):
        pass

    @abstractmethod
    def increment(self, key: str, amount: int = 1, **kwargs) -> Any:
        pass

    @abstractmethod
    def decrement(self, key: str, amount: int = 1, **kwargs) -> Any:
        pass

    @abstractmethod
    def add(self, key: str, value: Any, **kwargs) -> Any:
        pass

    @abstractmethod
    def remove(self, key: str, value: Any, **kwargs) -> Any:
        pass
