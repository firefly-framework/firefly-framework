from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

import firefly.domain as ffd


class Middleware(ABC):
    @abstractmethod
    def __call__(self, message: ffd.Message, next_: Callable) -> ffd.Message:
        pass
