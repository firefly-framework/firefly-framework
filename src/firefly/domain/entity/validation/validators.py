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

import re

# __pragma__('skip')
from abc import ABC, abstractmethod
from dateutil.parser import parse
from typing import Any
# __pragma__('noskip')
# __pragma__ ('ecom')
"""?
from firefly.presentation.web.polyfills import ABC, abstractmethod, Any
?"""
# __pragma__ ('noecom')


class Validation(ABC):
    def __init__(self, message: str = None):
        self.message = message

    @abstractmethod
    def __call__(self, value: Any, dto: dict) -> bool:
        pass


class IsType(Validation):
    def __init__(self, type_: Any, message: str = None):
        super().__init__(message or '{} must be of type ' + type_)
        self._type = type_

    def __call__(self, value: Any, dto: dict) -> bool:
        return isinstance(value, self._type)


class HasLength(Validation):
    def __init__(self, length: int, message: str = None):
        super().__init__(message or '{} must have a length of ' + str(length))
        self.length = length

    def __call__(self, value: Any, dto: dict) -> bool:
        return len(value) == self.length


class HasMaxLength(Validation):
    def __init__(self, length: int, message: str = None):
        super().__init__(message or '{} must have a length of ' + str(length))
        self.length = length

    def __call__(self, value: Any, dto: dict) -> bool:
        return len(value) <= self.length


class HasMinLength(Validation):
    def __init__(self, length: int, message: str = None):
        super().__init__(message or '{} must have a length of ' + str(length))
        self.length = length

    def __call__(self, value: Any, dto: dict) -> bool:
        return len(value) >= self.length


class Matches(Validation):
    def __init__(self, other_field: str, message: str = None):
        self._other_field = other_field
        super().__init__(message or '{} must match ' + other_field)

    def __call__(self, value: Any, dto: dict) -> bool:
        return value == dto[self._other_field]


class MatchesPattern(Validation):
    def __init__(self, pattern: str, message: str = None):
        super().__init__(message or '{} must match the pattern ' + pattern)
        self.regex = re.compile(pattern)

    def __call__(self, value: Any, dto: dict) -> bool:
        return self.regex.fullmatch(value) is not None


class IsValidEmail(MatchesPattern):
    def __init__(self, message: str = None):
        super().__init__(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            message or '{} must be a valid email address'
        )


class IsValidUrl(MatchesPattern):
    def __init__(self, message: str = None):
        super().__init__(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            message or '{} must be a valid url'
        )


class IsInt(MatchesPattern):
    def __init__(self, message: str = None):
        super().__init__(r'^\d+$', message or '{} must be an integer')

    def __call__(self, value: Any, dto: dict) -> bool:
        return isinstance(value, int) or (isinstance(value, str) and self.regex.fullmatch(value) is not None)


class IsFloat(MatchesPattern):
    def __init__(self, message: str = None):
        super().__init__(r'^\d+\.\d+$', message or '{} must be a float')

    def __call__(self, value: Any, dto: dict) -> bool:
        return isinstance(value, float) or (isinstance(value, str) and self.regex.fullmatch(value) is not None)


class IsNumeric(MatchesPattern):
    def __init__(self, message: str = None):
        super().__init__(r'^\d+\.?\d*$', message or '{} must be numeric')

    def __call__(self, value: Any, dto: dict) -> bool:
        return isinstance(value, (int, float)) or (isinstance(value, str) and self.regex.fullmatch(value) is not None)


class NumericValidation(Validation, ABC):
    def __init__(self, value: float, message: str = None):
        super().__init__(message)
        self.value = value

    @abstractmethod
    def __call__(self, value: Any, dto: dict) -> bool:
        pass


class IsMultipleOf(NumericValidation):
    def __call__(self, value: Any, dto: dict) -> bool:
        return value % self.value == 0


class IsLessThan(NumericValidation):
    def __call__(self, value: Any, dto: dict) -> bool:
        return value < self.value


class IsLessThanOrEqualTo(NumericValidation):
    def __call__(self, value: Any, dto: dict) -> bool:
        return value <= self.value


class IsGreaterThan(NumericValidation):
    def __call__(self, value: Any, dto: dict) -> bool:
        return value > self.value


class IsGreaterThanOrEqualTo(NumericValidation):
    def __call__(self, value: Any, dto: dict) -> bool:
        return value >= self.value


class IsDatetime(Validation):
    def __init__(self, message: str = None):
        super().__init__(message)

    def __call__(self, value: Any, dto: dict) -> bool:
        # __pragma__ ('ecom')
        """?
        return moment(value).isValid();
        ?"""
        # __pragma__ ('noecom')
        # __pragma__('skip')
        try:
            parse(value)
            return True
        except (ValueError, OverflowError):
            return False
        # __pragma__('noskip')


class IsOneOf(Validation):
    def __init__(self, values, message: str = None):
        super().__init__(message or '{} must be one of ' + str(values))
        self.values = values

    def __call__(self, value: Any, dto: dict) -> bool:
        values = self.values
        if callable(values):
            values = values(dto)
        return value in values
