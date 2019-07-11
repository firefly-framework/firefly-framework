from __future__ import annotations

from typing import get_type_hints
from dataclasses import dataclass, field, fields, MISSING
import firefly.domain as ffd


@dataclass()
class Message:
    headers: dict = field(default_factory=lambda: {}, init=False)

    def get_parameters(self):
        return ffd.get_arguments(self.__init__)
