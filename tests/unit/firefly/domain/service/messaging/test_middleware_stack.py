import pytest
from firefly import MiddlewareStack, Message


class MyMessage(Message):
    pass


def test_empty(sut):
    m = MyMessage()
    assert sut(m) is m


@pytest.fixture()
def sut():
    return MiddlewareStack([])
