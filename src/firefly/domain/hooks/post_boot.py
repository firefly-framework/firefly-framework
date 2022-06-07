from __future__ import annotations

from abc import ABC, abstractmethod


class PostBoot(ABC):
    """
    Run this code after the boot sequence is complete.
    """
    @abstractmethod
    def __call__(self, kernel):
        pass
