from dataclasses import dataclass, MISSING

import pytest
from firefly import Event


def test_event(sut):
    assert sut.context == 'test_event'
    assert str(sut) == 'test_event.TestEvent'


@dataclass
class TestEvent(Event):
    foo: str = MISSING


@pytest.fixture()
def sut():
    return TestEvent('bar')
