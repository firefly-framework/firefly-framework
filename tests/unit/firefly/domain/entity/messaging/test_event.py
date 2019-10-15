import pytest
from firefly import Event, required


def test_event(sut):
    assert sut._context == 'test_event'
    assert str(sut) == 'test_event.ThisEvent'


class ThisEvent(Event):
    foo: str = required()


@pytest.fixture()
def sut():
    return ThisEvent(foo='bar')
