from __future__ import annotations

from .message import Message


class Event(Message):
    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.context = self.__module__.split('.')[0]

    @property
    def context(self):
        return self.get('context')

    @context.setter
    def context(self, value: str):
        self.header('context', value)

    def __str__(self):
        return '{}.{}'.format(self.context, self.__name__) if self.context is not None else type(self).__name__

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, str) and other == str(self):
            return True
        try:
            return isinstance(self, other)
        except TypeError:
            return False
