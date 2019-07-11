import pytest
from firefly import Message


@pytest.fixture()
def sut():
    return Message()
