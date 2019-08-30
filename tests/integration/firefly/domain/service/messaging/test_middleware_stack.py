from typing import Callable

import pytest
from firefly import MiddlewareStack, Middleware, Message, Command


def test_order(sut):
    result = sut(Command())
    assert result.headers['numbers'] == [1, 2, 3]


@pytest.fixture()
def sut():
    class AppendNumber(Middleware):
        def __init__(self, number: int):
            self.number = number

        def __call__(self, message: Message, next_: Callable, *args, **kwargs):
            if 'numbers' not in message.headers:
                message.headers['numbers'] = []
            message.headers['numbers'].append(self.number)
            return next_(message)

    return MiddlewareStack([
        AppendNumber(1),
        AppendNumber(2),
        AppendNumber(3),
    ])
