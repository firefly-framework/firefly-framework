import pytest
from firefly import MiddlewareStack, Message


def test_empty(sut):
    m = Message()
    assert sut(m) is m


@pytest.fixture()
def sut():
    return MiddlewareStack([])
